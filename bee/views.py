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

    # Check if the anime is in the watchlist
    user = request.user
    watchlist_item = await sync_to_async(WatchList.objects.filter)(user=user, anime_id=anime_id)
    unwatched = await sync_to_async(watchlist_item.exists)()


    comments = await sync_to_async(Comment_anime.objects.filter)(anime_id=anime_id)
    comment_form = CommentFormAnime()
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        
        if post_type == 'comment':
            comment_form = CommentFormAnime(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.anime_id = anime_id
                await sync_to_async(setattr)(new_comment, 'user', request.user)
                new_comment.created_at = await sync_to_async(timezone.now)()
                await sync_to_async(new_comment.save)()
                return HttpResponseRedirect(request.path_info)
        
        elif post_type == 'reaction':
            reaction_type = request.POST.get('reaction_type')
            # Use sync_to_async to create or update the reaction asynchronously
            reaction, created = await sync_to_async(Reaction_anime.objects.get_or_create)(
                user=request.user,
                anime_id=anime_id,
            )
            # Update the reaction type based on the hidden input
            if reaction_type == 'like':
                reaction.reaction_type = Reaction_anime.LIKE
            elif reaction_type == 'dislike':
                reaction.reaction_type = Reaction_anime.DISLIKE
            await sync_to_async(reaction.save)()

        elif post_type == 'watchlater':
            anime_id = request.POST.get('anime_id')  # Use get() to avoid KeyError
            user = request.user

            watchlist_item = await sync_to_async(WatchList.objects.filter)(user=user, anime_id=anime_id)
            if await sync_to_async(watchlist_item.exists)():  # If this anime is already marked as unwatch
                await sync_to_async(watchlist_item.delete)()  # Remove it from watchlist
                unwatched = False  # Set its unwatch status to False
            else: 
                watchlist_item, created = await sync_to_async(WatchList.objects.get_or_create)(user=user, anime_id=anime_id)  # Add it to watchlist or get it if it already exists
                unwatched = True  # Set its unwatch status to True only if it was created
            return HttpResponseRedirect(request.path_info)
    else:
        comment_form = CommentFormAnime()

    likes = await sync_to_async(Reaction_anime.objects.filter(anime_id=anime_id, reaction_type=Reaction_anime.LIKE).count)()
    dislikes = await sync_to_async(Reaction_anime.objects.filter(anime_id=anime_id, reaction_type=Reaction_anime.DISLIKE).count)()

    response = await sync_to_async(render)(request, 'anime/anime_details.html', {
                                                        'anime': anime, 'genres': genres, 
                                                        'streaming_links':streaming_links,
                                                        'unwatch': unwatched,
                                                        'comment_form': comment_form,
                                                        'comments':comments,
                                                        'likes':likes,
                                                        'dislikes':dislikes,
                                                        })
    return response


async def get_manga(request, manga_id):
    client = kitsu.Client()
    manga = await client.get_manga(manga_id)

    # Fetch genres and await the coroutine
    genres = [genre.title for genre in await manga.categories]

    # Check if the anime is in the watchlist
    user = request.user
    readlist_item = await sync_to_async(ReadList.objects.filter)(user=user, manga_id=manga_id)
    unread = await sync_to_async(readlist_item.exists)()


    comments = await sync_to_async(Comment_manga.objects.filter)(manga_id=manga_id)
    comment_form = CommentFormManga()
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        
        if post_type == 'comment':
            comment_form = CommentFormManga(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.manga_id = manga_id
                await sync_to_async(setattr)(new_comment, 'user', request.user)
                new_comment.created_at = await sync_to_async(timezone.now)()
                await sync_to_async(new_comment.save)()
                return HttpResponseRedirect(request.path_info)
        
        elif post_type == 'reaction':
            reaction_type = request.POST.get('reaction_type')
            # Use sync_to_async to create or update the reaction asynchronously
            reaction, created = await sync_to_async(Reaction_manga.objects.get_or_create)(
                user=request.user,
                manga_id=manga_id,
            )
            # Update the reaction type based on the hidden input
            if reaction_type == 'like':
                reaction.reaction_type = Reaction_manga.LIKE
            elif reaction_type == 'dislike':
                reaction.reaction_type = Reaction_manga.DISLIKE
            await sync_to_async(reaction.save)()

        elif post_type == 'readlater':
            manga_id = request.POST.get('manga_id')  # Use get() to avoid KeyError
            user = request.user

            readlist_item = await sync_to_async(ReadList.objects.filter)(user=user, manga_id=manga_id)
            if await sync_to_async(readlist_item.exists)():  # If this anime is already marked as unwatch
                await sync_to_async(readlist_item.delete)()  # Remove it from watchlist
                unread = False  # Set its unwatch status to False
            else: 
                readlist_item, created = await sync_to_async(ReadList.objects.get_or_create)(user=user, manga_id=manga_id)  # Add it to watchlist or get it if it already exists
                unread = True  # Set its unwatch status to True only if it was created
            return HttpResponseRedirect(request.path_info)
    else:
        comment_form = CommentFormManga()

    likes = await sync_to_async(Reaction_manga.objects.filter(manga_id=manga_id, reaction_type=Reaction_manga.LIKE).count)()
    dislikes = await sync_to_async(Reaction_manga.objects.filter(manga_id=manga_id, reaction_type=Reaction_manga.DISLIKE).count)()

    response = await sync_to_async(render)(request, 'manga/manga_details.html', {
                                                        'manga': manga, 'genres': genres, 
                                                        'unread': unread,
                                                        'comment_form': comment_form,
                                                        'comments':comments,
                                                        'likes':likes,
                                                        'dislikes':dislikes,
                                                        })
    return response


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