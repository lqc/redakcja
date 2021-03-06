import os
import functools
import logging
logger = logging.getLogger("fnp.wiki")

from django.conf import settings

from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_POST, require_GET
from django.core.urlresolvers import reverse
from wiki.helpers import (JSONResponse, JSONFormInvalid, JSONServerError,
                ajax_require_permission, recursive_groupby)
from django import http

from wiki.models import getstorage, DocumentNotFound, normalize_name, split_name, join_name, Theme
from wiki.forms import DocumentTextSaveForm, DocumentTagForm, DocumentCreateForm, DocumentsUploadForm
from datetime import datetime
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import decorator_from_middleware
from django.middleware.gzip import GZipMiddleware


#
# Quick hack around caching problems, TODO: use ETags
#
from django.views.decorators.cache import never_cache

import wlapi
import nice_diff
import operator

MAX_LAST_DOCS = 10


def normalized_name(view):

    @functools.wraps(view)
    def decorated(request, name, *args):
        normalized = normalize_name(name)
        logger.debug('View check %r -> %r', name, normalized)

        if normalized != name:
            return http.HttpResponseRedirect(
                        reverse('wiki_' + view.__name__, kwargs={'name': normalized}))

        return view(request, name, *args)

    return decorated


@never_cache
def document_list(request):
    return direct_to_template(request, 'wiki/document_list.html', extra_context={
        'docs': getstorage().all(),
        'last_docs': sorted(request.session.get("wiki_last_docs", {}).items(),
                        key=operator.itemgetter(1), reverse=True),
    })


@never_cache
@normalized_name
def editor(request, name, template_name='wiki/document_details.html'):
    storage = getstorage()

    try:
        document = storage.get(name)
    except DocumentNotFound:
        return http.HttpResponseRedirect(reverse("wiki_create_missing", args=[name]))

    access_time = datetime.now()
    last_documents = request.session.get("wiki_last_docs", {})
    last_documents[name] = access_time

    if len(last_documents) > MAX_LAST_DOCS:
        oldest_key = min(last_documents, key=last_documents.__getitem__)
        del last_documents[oldest_key]
    request.session['wiki_last_docs'] = last_documents

    return direct_to_template(request, template_name, extra_context={
        'document': document,
        'document_name': document.name,
        'document_info': document.info,
        'document_meta': document.meta,
        'forms': {
            "text_save": DocumentTextSaveForm(prefix="textsave"),
            "add_tag": DocumentTagForm(prefix="addtag"),
        },
        'REDMINE_URL': settings.REDMINE_URL,
    })


@require_GET
@normalized_name
def editor_readonly(request, name, template_name='wiki/document_details_readonly.html'):
    name = normalize_name(name)
    storage = getstorage()

    try:
        revision = request.GET['revision']
        document = storage.get(name, revision)
    except (KeyError, DocumentNotFound):
        raise http.Http404

    access_time = datetime.now()
    last_documents = request.session.get("wiki_last_docs", {})
    last_documents[name] = access_time

    if len(last_documents) > MAX_LAST_DOCS:
        oldest_key = min(last_documents, key=last_documents.__getitem__)
        del last_documents[oldest_key]
    request.session['wiki_last_docs'] = last_documents

    return direct_to_template(request, template_name, extra_context={
        'document': document,
        'document_name': document.name,
        'document_info': dict(document.info(), readonly=True),
        'document_meta': document.meta,
        'REDMINE_URL': settings.REDMINE_URL,
    })


@normalized_name
def create_missing(request, name):
    storage = getstorage()

    if request.method == "POST":
        form = DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            doc = storage.create_document(
                name=form.cleaned_data['id'],
                text=form.cleaned_data['text'],
            )

            return http.HttpResponseRedirect(reverse("wiki_editor", args=[doc.name]))
    else:
        form = DocumentCreateForm(initial={
                "id": name.replace(" ", "_"),
                "title": name.title(),
        })

    return direct_to_template(request, "wiki/document_create_missing.html", extra_context={
        "document_name": name,
        "form": form,
    })


def upload(request):
    storage = getstorage()

    if request.method == "POST":
        form = DocumentsUploadForm(request.POST, request.FILES)
        if form.is_valid():
            zip = form.cleaned_data['zip']
            skipped_list = []
            ok_list = []
            error_list = []
            titles = {}
            existing = storage.all()
            for filename in zip.namelist():
                if filename[-1] == '/':
                    continue
                title = normalize_name(os.path.basename(filename)[:-4])
                if not (title and filename.endswith('.xml')):
                    skipped_list.append(filename)
                elif title in titles:
                    error_list.append((filename, title, _('Title already used for %s' % titles[title])))
                elif title in existing:
                    error_list.append((filename, title, _('Title already used in repository.')))
                else:
                    try:
                        zip.read(filename).decode('utf-8') # test read
                        ok_list.append((filename, title))
                    except UnicodeDecodeError:
                        error_list.append((filename, title, _('File should be UTF-8 encoded.')))
                    titles[title] = filename

            if not error_list:
                for filename, title in ok_list:
                    storage.create_document(
                        name=title,
                        text=zip.read(filename).decode('utf-8')
                    )

            return direct_to_template(request, "wiki/document_upload.html", extra_context={
                "form": form,
                "ok_list": ok_list,
                "skipped_list": skipped_list,
                "error_list": error_list,
            })
    else:
        form = DocumentsUploadForm()

    return direct_to_template(request, "wiki/document_upload.html", extra_context={
        "form": form,
    })


@never_cache
@normalized_name
@decorator_from_middleware(GZipMiddleware)
def text(request, name):
    storage = getstorage()

    if request.method == 'POST':
        form = DocumentTextSaveForm(request.POST, prefix="textsave")
        if form.is_valid():
            revision = form.cleaned_data['parent_revision']
            document = storage.get_or_404(name, revision)
            document.text = form.cleaned_data['text']
            comment = form.cleaned_data['comment']
            if form.cleaned_data['stage_completed']:
                comment += '\n#stage-finished: %s\n' % form.cleaned_data['stage_completed']
            if request.user.is_authenticated():
                author_name = request.user
                author_email = request.user.email
            else:
                author_name = form.cleaned_data['author_name']
                author_email = form.cleaned_data['author_email']
            author = "%s <%s>" % (author_name, author_email)
            storage.put(document, author=author, comment=comment, parent=revision)
            document = storage.get(name)
            return JSONResponse({
                'text': document.plain_text if revision != document.revision else None,
                'meta': document.meta(),
                'revision': document.revision,
            })
        else:
            return JSONFormInvalid(form)
    else:
        revision = request.GET.get("revision", None)

        try:
            try:
                revision = revision and int(revision)
                logger.info("Fetching %s", revision)
                document = storage.get(name, revision)
            except ValueError:
                # treat as a tag
                logger.info("Fetching tag %s", revision)
                document = storage.get_by_tag(name, revision)
        except DocumentNotFound:
            raise http.Http404

        return JSONResponse({
            'text': document.plain_text,
            'meta': document.meta(),
            'revision': document.revision,
        })


@never_cache
@normalized_name
@require_POST
@ajax_require_permission('wiki.can_revert_changes')
def revert(request, name):
    storage = getstorage()
    revision = request.POST['target_revision']

    author = "{0.username} <{0.email}>".format(request.user)

    try:
        document = storage.revert(name, revision, author=author)

        return JSONResponse({
            'text': document.plain_text if revision != document.revision else None,
            'meta': document.meta(),
            'revision': document.revision,
        })
    except DocumentNotFound:
        raise http.Http404

@never_cache
def gallery(request, directory):
    try:
        base_url = ''.join((
                        smart_unicode(settings.MEDIA_URL),
                        smart_unicode(settings.FILEBROWSER_DIRECTORY),
                        smart_unicode(directory)))

        base_dir = os.path.join(
                    smart_unicode(settings.MEDIA_ROOT),
                    smart_unicode(settings.FILEBROWSER_DIRECTORY),
                    smart_unicode(directory))

        def map_to_url(filename):
            return "%s/%s" % (base_url, smart_unicode(filename))

        def is_image(filename):
            return os.path.splitext(f)[1].lower() in (u'.jpg', u'.jpeg', u'.png')

        images = [map_to_url(f) for f in map(smart_unicode, os.listdir(base_dir)) if is_image(f)]
        images.sort()
        return JSONResponse(images)
    except (IndexError, OSError):
        logger.exception("Unable to fetch gallery")
        raise http.Http404


@never_cache
@normalized_name
def diff(request, name):
    storage = getstorage()

    revA = int(request.GET.get('from', 0))
    revB = int(request.GET.get('to', 0))

    if revA > revB:
        revA, revB = revB, revA

    if revB == 0:
        revB = None

    docA = storage.get_or_404(name, int(revA))
    docB = storage.get_or_404(name, int(revB))

    return http.HttpResponse(nice_diff.html_diff_table(docA.plain_text.splitlines(),
                                         docB.plain_text.splitlines(), context=3))


@never_cache
@normalized_name
def history(request, name):
    storage = getstorage()

    # TODO: pagination
    changesets = list(storage.history(name))

    return JSONResponse(changesets)


@require_POST
@ajax_require_permission('wiki.can_change_tags')
def add_tag(request, name):
    name = normalize_name(name)
    storage = getstorage()

    form = DocumentTagForm(request.POST, prefix="addtag")
    if form.is_valid():
        doc = storage.get_or_404(form.cleaned_data['id'])
        doc.add_tag(tag=form.cleaned_data['tag'],
                    revision=form.cleaned_data['revision'],
                    author=request.user.username)
        return JSONResponse({"message": _("Tag added")})
    else:
        return JSONFormInvalid(form)


@require_POST
@ajax_require_permission('wiki.can_publish')
def publish(request, name):
    name = normalize_name(name)

    storage = getstorage()
    document = storage.get_by_tag(name, "ready_to_publish")

    api = wlapi.WLAPI(**settings.WL_API_CONFIG)

    try:
        return JSONResponse({"result": api.publish_book(document)})
    except wlapi.APICallException, e:
        return JSONServerError({"message": str(e)})


def themes(request):
    prefix = request.GET.get('q', '')
    return http.HttpResponse('\n'.join([str(t) for t in Theme.objects.filter(name__istartswith=prefix)]))
