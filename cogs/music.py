import disnake
from disnake import FFmpegPCMAudio
from disnake.ext import commands
from core.any import CogExtension
import functools
from youtube_dl import YoutubeDL
import asyncio
import queue

playlist = queue.Queue()
download_queue = queue.Queue()
play_next_song = asyncio.Event()


# only supports one guild play music at one time
class Music(CogExtension):
    async def raw_search(self, query):
        loop = self.bot.loop
        with YoutubeDL({"extract_flat": True, "noplaylist": True, "quiet": True, 'default_search': 'ytsearch'}) as ydl:
            partial = functools.partial(ydl.extract_info, query, download=False)
            info = await loop.run_in_executor(None, partial)
        if "_type" in info:
            if info["_type"] == "playlist":
                return (2, info)  # playlist
            else:
                if "id" in info:
                    return (0, info)    # a video but in list
                else:
                    return (1, info)    # is ytsearch
        else:
            return (0, info)  # only single video

    async def get_video(self, query):
        loop = self.bot.loop
        with YoutubeDL({"format": "bestaudio", "noplaylist": True, 'quiet': True, 'default_search': 'ytsearch'}) as ydl:
            partial = functools.partial(ydl.extract_info, query, download=False)
            info = await loop.run_in_executor(None, partial)
        if "entries" in info:
            return (info["entries"][0], info["entries"][0]["url"])
        else:
            return (info, info["url"])

    @staticmethod
    async def join(inter, voice):
        channel = inter.author.voice.channel

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
        return voice

    async def player(self, inter):
        # Solves a problem
        FFMPEG_OPTS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
        voice = disnake.utils.get(self.bot.voice_clients, guild=inter.guild)
        voice = await self.join(inter, voice)
        event = asyncio.Event()
        event.set()
        while True:
            await event.wait()
            event.clear()
            if playlist.empty():
                await inter.followup.send("所有歌曲已撥放完畢")
                break
            if not voice.is_connected():
                playlist.queue.clear()
                download_queue.queue.clear()
                break
            video, source = playlist.get()
            await inter.followup.send(f"Now playing ***{video['title']}***.")
            voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: event.set())
            if not download_queue.empty():
                video, source = await self.get_video(download_queue.get())
                playlist.put((video, source))

    async def check(self, query):
        if playlist.empty() and not download_queue.empty():
            download_queue.put(query)
            video, source = await self.get_video(download_queue.get())
            playlist.put((video, source))
        elif playlist.empty() and download_queue.empty():
            video, source = await self.get_video(query)
            playlist.put((video, source))
        else:
            download_queue.put(query)

    @commands.slash_command(description="播放音樂", dm_permission=False)
    async def play(self, inter, query: str = commands.Param(name="yt網址或歌名")):
        if inter.author.voice is None:
            await inter.response.send_message("請先進入語音頻道", ephemeral=True)
            return
        playing = False
        for vc in self.bot.voice_clients:
            if vc.guild.id == inter.guild.id:
                if vc.channel.id != inter.author.voice.channel.id:
                    await inter.response.send_message(f"正在<#{vc.channel.id}>被使用中")
                    return
                else:
                    playing = True
                    break
        await inter.response.defer()

        if playing:
            query_type, info = await self.raw_search(query)
            if query_type == 0:
                query = "https://www.youtube.com/watch?v=" + info["id"]
                await self.check(query)
            elif query_type == 1:
                await self.check(query)
            elif query_type == 2:
                first = True
                for entry in info["entries"]:
                    query = "https://www.youtube.com/watch?v=" + entry["id"]
                    if first:
                        await self.check(query)
                        first = False
                    else:
                        download_queue.put(query)
        else:
            query_type, info = await self.raw_search(query)
            if query_type == 0:
                query = "https://www.youtube.com/watch?v=" + info["id"]
                video, source = await self.get_video(query)
                playlist.put((video, source))
                await self.player(inter)
            elif query_type == 1:
                video, source = await self.get_video(query)
                playlist.put((video, source))
                await self.player(inter)
            elif query_type == 2:
                first = True
                for entry in info["entries"]:
                    query = "https://www.youtube.com/watch?v=" + entry["id"]
                    if first:
                        video, source = await self.get_video(query)
                        playlist.put((video, source))
                        first = False
                    else:
                        download_queue.put(query)
                await self.player(inter)


def setup(bot):
    bot.add_cog(Music(bot))
