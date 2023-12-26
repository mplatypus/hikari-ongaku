from . import error, abc, enums
import typing as t

import hikari
import aiohttp
import logging

if t.TYPE_CHECKING:
    from .ongaku import Ongaku


class InternalSession:
    def __init__(self, ongaku: Ongaku) -> None:
        self._ongaku = ongaku

    async def update_session(self, session_id: str) -> abc.Session:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._ongaku.internal.uri + "/sessions/" + session_id,
                headers=self._ongaku.internal.headers,
            ) as response:
                if response.status >= 400:
                    raise error.ResponseException(response.status)

                try:
                    session_model = abc.Session.as_payload(await response.json())
                except Exception as e:
                    raise error.BuildException(e)

                return session_model


class InternalPlayer:
    """
    The Rest based actions for the player.
    """

    def __init__(self, ongaku: Ongaku) -> None:
        self._ongaku = ongaku

    async def fetch_players(self, session_id: str) -> t.Optional[list[abc.Player]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._ongaku.internal.uri + "/sessions/" + session_id + "/players",
                headers=self._ongaku.internal.headers,
            ) as response:
                if response.status >= 400:
                    raise error.ResponseException(response.status)

                players = await response.json()

                player_list: list[abc.Player] = []

                for player in players:
                    try:
                        player_model = abc.Player.as_payload(player)
                    except Exception as e:
                        raise error.BuildException(e)

                    player_list.append(player_model)

        return player_list

    async def fetch_player(
        self, session_id: str, guild_id: hikari.Snowflake
    ) -> t.Optional[abc.Player]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._ongaku.internal.uri
                + "/sessions/"
                + session_id
                + "/players/"
                + str(guild_id),
                headers=self._ongaku.internal.headers,
            ) as response:
                if response.status >= 400:
                    raise error.ResponseException(response.status)

                try:
                    player_model = abc.Player.as_payload(await response.json())
                except Exception as e:
                    raise error.BuildException(e)

        return player_model

    async def update_player(
        self,
        guild_id: hikari.Snowflake,
        session_id: str,
        *,
        track: hikari.UndefinedNoneOr[abc.Track] = hikari.UNDEFINED,
        position: hikari.UndefinedOr[int] = hikari.UNDEFINED,
        end_time: hikari.UndefinedOr[int] = hikari.UNDEFINED,
        volume: hikari.UndefinedOr[int] = hikari.UNDEFINED,
        paused: hikari.UndefinedOr[bool] = hikari.UNDEFINED,
        voice: hikari.UndefinedOr[abc.Voice] = hikari.UNDEFINED,
        no_replace: bool = True,
    ) -> abc.Player:
        """
        Update a player

        Updates a player with the new parameters, or creates a new one if none exist.

        Parameters
        ----------
        guild_id : hikari.Snowflake
            The guild id that the bot is playing in.
        session_id : str
            The session_id for the lavalink server session.

        """
        patch_data: dict[str, t.Any] = {}

        if track != hikari.UNDEFINED:
            if track == None:
                patch_data.update(
                    {
                        "track": {
                            "encoded": None,
                        }
                    }
                )
            else:
                patch_data.update(
                    {
                        "track": {
                            "encoded": track.encoded,
                        }
                    }
                )

        if position != hikari.UNDEFINED:
            patch_data.update({"position": position})

        if end_time != hikari.UNDEFINED:
            patch_data.update({"endTime": end_time})

        if volume != hikari.UNDEFINED:
            patch_data.update({"volume": volume})

        if paused != hikari.UNDEFINED:
            patch_data.update({"paused": paused})

        if voice != hikari.UNDEFINED:
            patch_data.update(
                {
                    "voice": {
                        "token": voice.token,
                        "endpoint": voice.endpoint,
                        "sessionId": voice.session_id,
                    }
                }
            )

        new_headers = self._ongaku.internal.headers.copy()

        new_headers.update({"Content-Type": "application/json"})

        params = {"noReplace": "false"}

        if no_replace:
            params.update({"noReplace": "false"})

        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(
                    self._ongaku.internal.uri
                    + "/sessions/"
                    + session_id
                    + "/players/"
                    + str(guild_id),
                    headers=new_headers,
                    params=params,
                    json=patch_data,
                ) as response:
                    # if response.status >= 400:
                    #    raise error.ResponseException(response.status)

                    try:
                        player_model = abc.Player.as_payload(await response.json())
                    except Exception as e:
                        raise error.BuildException(e)
            except Exception as e:
                raise e

        return player_model

    async def delete_player(self, session_id: str, guild_id: hikari.Snowflake) -> None:
        """
        Creates a new player for the specified guild. If one already exists, returns that instead.
        """
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                self._ongaku.internal.uri
                + "/sessions/"
                + session_id
                + "/players/"
                + str(guild_id),
                headers=self._ongaku.internal.headers,
            ) as response:
                if response.status >= 400:
                    raise error.ResponseException(response.status)


class InternalTrack:
    """
    The rest based actions for the track.
    """

    def __init__(self, ongaku: Ongaku) -> None:
        self._ongaku: Ongaku = ongaku

    async def load_track(
        self, platform: enums.PlatformType, query: str
    ) -> t.Optional[list[abc.Track]]:
        async with aiohttp.ClientSession() as session:
            if platform == enums.PlatformType.YOUTUBE:
                params = {"identifier": f'ytsearch:"{query}"'}
            elif platform == enums.PlatformType.YOUTUBE_MUSIC:
                params = {"identifier": f'ytmsearch:"{query}"'}
            elif platform == enums.PlatformType.SPOTIFY:
                params = {"identifier": f'scsearch:"{query}"'}
            else:
                params = {"identifier": f'scsearch:"{query}"'}

            async with session.get(
                self._ongaku.internal.uri + "/loadtracks",
                headers=self._ongaku.internal.headers,
                params=params,
            ) as response:
                if response.status >= 400:
                    raise error.ResponseException(response.status)

                data = await response.json()

                load_type = data["loadType"]

                if load_type == "search":
                    tracks: list[abc.Track] = []

                    for t in data["data"]:
                        try:
                            track = abc.Track.as_payload(t)
                        except Exception as e:
                            logging.error("Failed to build track: " + str(e))
                            continue

                        tracks.append(track)

                    if len(tracks) <= 0:
                        return

                    else:
                        return tracks


class Internal:
    def __init__(self, ongaku: Ongaku) -> None:
        self._ongaku: Ongaku = ongaku

        self._internal_session = InternalSession(self._ongaku)

        self._internal_player = InternalPlayer(self._ongaku)

        self._internal_track = InternalTrack(self._ongaku)

    @property
    def session(self) -> InternalSession:
        return self._internal_session

    @property
    def player(self) -> InternalPlayer:
        return self._internal_player

    @property
    def track(self) -> InternalTrack:
        return self._internal_track


class RestApi:
    """
    The base rest class for all rest related things.
    """

    def __init__(self, ongaku: Ongaku) -> None:
        self._ongaku: Ongaku = ongaku

        self._internal = Internal(self._ongaku)

    @property
    def internal(self) -> Internal:
        return self._internal

    async def fetch_info(self) -> abc.Info:
        """
        Fetch the information about the Lavalink server.

        ----
        Returns: Returns a
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._ongaku.internal.uri + "/info",
                headers=self._ongaku.internal.headers,
            ) as response:
                if response.status >= 400:
                    raise error.ResponseException(response.status)

                try:
                    info_resp = abc.Info.as_payload(await response.json())
                except Exception as e:
                    raise error.BuildException(e)

        return info_resp

    async def search(
        self, platform: enums.PlatformType, query: str
    ) -> t.Optional[list[abc.Track]]:
        return await self.internal.track.load_track(platform, query)
