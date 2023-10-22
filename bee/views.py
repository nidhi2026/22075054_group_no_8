from django.shortcuts import render, redirect
import kitsu
from .models import *
from .forms import *
from asgiref.sync import sync_to_async
from django.http import HttpResponseRedirect
from django.utils import timezone


# Create your views here.
async def trending(request):
    client = kitsu.Client()
    tre_animes = await client.trending_anime()
    animes = [{'id': anime.id, 'title': anime.title} for anime in tre_animes]

    fantasy_genre = await client.search_anime(genres=['fantasy'], limit=10)
    fantasy = [{'id': anime.id, 'title': anime.title} for anime in fantasy_genre]

    genres_list = [ "Action","Adventure","Comedy","Fantasy","Horror","Mecha","Music","Mystery","Psychological","Romance","Sci-Fi","Slice of Life","Sports","Supernatural","Thriller"]

    return render(request, 'trends.html', {'animes': animes, 'fantasy':fantasy, 'genres':genres_list})

async def get_anime(request, anime_id):
    client = kitsu.Client()
    anime = await client.get_anime(anime_id)

    # Fetch genres and await the coroutine
    genres = [genre.title for genre in await anime.categories]
    streaming_links = [{'title':streams.title,'url':streams.url} for streams in await anime.streaming_links]

    def get_unwatch_status(anime_id):
        unwatch = request.session.get('unwatch', {})
        if isinstance(unwatch, bool):  # If unwatch is a boolean
            unwatch = {}  # Initialize it as an empty dictionary
        request.session['unwatch'] = unwatch
        request.session.save()
        return unwatch.get(anime_id, False)

    # Call the synchronous function using sync_to_async
    unwatch = await sync_to_async(get_unwatch_status)(anime_id)
    unwatche = (request.session.get('unwatch', {}))
    if(unwatche.get(str(anime_id))!=None):
        unwatched = unwatche[str(anime_id)]
    else:
        unwatched=False

    # comments = await sync_to_async(Comment.objects.filter)(id=anime_id, parent=None)

    # if request.method == 'POST':
    #     comment_form = CommentForm(data=request.POST)
    #     if comment_form.is_valid():
    #         new_comment = comment_form.save(commit=False)
    #         new_comment.id = anime_id
    #         # Assign the comment to a parent if it exists in the form
    #         parent_id = request.POST.get('parent_id')
    #         if parent_id:
    #             new_comment.parent_id = parent_id
    #         await sync_to_async(setattr)(new_comment, 'user', request.user)
    #         new_comment.created_at = await sync_to_async(timezone.now)()
    #         await sync_to_async(new_comment.save)()
    #         return HttpResponseRedirect(request.path_info)
    # else:
    #     comment_form = CommentForm()
    # return render(request, 'anime/anime_details.html', context={
    #                                                     'anime': anime, 'genres': genres, 
    #                                                     'streaming_links':streaming_links,
    #                                                     'unwatch': unwatched,
    #                                                     'comments': comments,
    #                                                     'comment_form': comment_form,
    #                                                     })
    response = await sync_to_async(render)(request, 'anime/anime_details.html', {
                                                        'anime': anime, 'genres': genres, 
                                                        'streaming_links':streaming_links,
                                                        'unwatch': unwatched,
                                                        # 'comments': comments,
                                                        # 'comment_form': comment_form,
                                                        })

    return response


async def get_manga(request, manga_id):
    client = kitsu.Client()
    manga = await client.get_manga(manga_id)

    # Fetch genres and await the coroutine
    genres = [genre.title for genre in await manga.categories]

    # Define a synchronous function to interact with the session
    def get_unread_status(manga_id):
        unread = request.session.get('unread', {})
        if isinstance(unread, bool):  # If unwatch is a boolean
            unread = {}  # Initialize it as an empty dictionary
        request.session['unread'] = unread
        request.session.save()
        return unread.get(manga_id, False)

    # Call the synchronous function using sync_to_async
    unread = await sync_to_async(get_unread_status)(manga_id)
    unrede = (request.session.get('unread', {}))
    if(unrede.get(str(manga_id))!=None):
        unred = unrede[str(manga_id)]
    else:
        unred=False

    return render(request, 'manga/manga_details.html', context={
                                                        'manga': manga, 'genres': genres, 
                                                        'unread': unred,
                                                        })


async def get_genre_anime(request, genre):
    client = kitsu.Client()
    animes = await client.search_anime(genres=[genre.lower()], limit=20)
    genre_anime = [{'id': anime.id, 'title': anime.title} for anime in animes if anime.title!=None]

    return render(request, 'anime/genre_anime.html', context={'genre_anime':genre_anime, 'genre':genre})

async def get_genre_manga(request, genre):
    client = kitsu.Client()
    mangas = await client.search_manga(genres=[genre.lower()], limit=20)
    genre_manga = [{'id': manga.id, 'title': manga.title} for manga in mangas if manga.title!=None]

    return render(request, 'manga/genre_manga.html', context={'genre_manga':genre_manga, 'genre':genre})

def in_watchlater(request):
    if request.method == "POST":
        anime_id = request.POST.get('anime_id')  # Use get() to avoid KeyError
        user = request.user
        unwatch = request.session.get('unwatch', {})  # Get the unwatch dictionary from the session

        if isinstance(unwatch, bool):  # If unwatch is a boolean
            unwatch = {}  # Initialize it as an empty dictionary

        if anime_id in unwatch and unwatch[anime_id]:  # If this anime is already marked as unwatch
            WatchList.objects.filter(user=user, anime_id=anime_id).delete()  # Remove it from watchlist
            unwatch[anime_id] = False  # Set its unwatch status to False
        else: 
            watchlist_item, created = WatchList.objects.get_or_create(user=user, anime_id=anime_id)  # Add it to watchlist or get it if it already exists
            if created:
                unwatch[anime_id] = True  # Set its unwatch status to True only if it was created
        # Store unwatch in session
        request.session['unwatch'] = unwatch
        request.session.modified = True

        return redirect('get_anime', anime_id=anime_id)

def in_readlater(request):
    if request.method == "POST":
        manga_id = request.POST.get('manga_id')  # Use get() to avoid KeyError
        user = request.user
        unread = request.session.get('unread', {})  # Get the unread dictionary from the session

        if isinstance(unread, bool):  # If unread is a boolean
            unread = {}  # Initialize it as an empty dictionary

        if manga_id in unread and unread[manga_id]:  # If this mn=anga is already marked as unread
            WatchList.objects.filter(user=user, manga_id=manga_id).delete()  # Remove it from readlist
            unread[manga_id] = False  # Set its unread status to False
        else: 
            readlist_item, created = ReadList.objects.get_or_create(user=user, manga_id=manga_id)  # Add it to readlist or get it if it already exists
            if created:
                unread[manga_id] = True  # Set its unread status to True only if it was created
        # Store unread in session
        request.session['unread'] = unread
        request.session.modified = True

        return redirect('get_manga', manga_id=manga_id)

async def watchlist(request):
    # Define a synchronous function to fetch data from the database
    def fetch_data():
        watchlater = WatchList.objects.filter(user=request.user)
        return [anime.anime_id for anime in watchlater]

    # Call the synchronous function using sync_to_async
    data = await sync_to_async(fetch_data)()
    watchlist = []

    client = kitsu.Client()
    for anime_id in data:
        a = await client.get_anime(anime_id)
        watchlist.append({'anime_id':anime_id, 'title':a.title, 'image':a.poster_image(_type='small')})
    watchlist=watchlist[::-1]

    render_func = sync_to_async(render, thread_sensitive=True)
    return await render_func(request, 'anime/watchlist.html', {'watchlater': watchlist})

async def readlist(request):
    # Define a synchronous function to fetch data from the database
    def fetch_data():
        readlater = ReadList.objects.filter(user=request.user)
        return [manga.manga_id for manga in readlater]

    # Call the synchronous function using sync_to_async
    data = await sync_to_async(fetch_data)()
    readlist = []

    client = kitsu.Client()
    for manga_id in data:
        a = await client.get_manga(manga_id)
        readlist.append({'manga_id':manga_id, 'title':a.title, 'image':a.poster_image})
    readlist=readlist[::-1]

    render_func = sync_to_async(render, thread_sensitive=True)
    return await render_func(request, 'manga/readlist.html', {'readlater': readlist})