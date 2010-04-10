import config
import pylast

def get_similar(artist_name):
    network = pylast.get_lastfm_network(api_key = config.LAST_FM_API_KEY,
                                        api_secret = config.LAST_FM_API_KEY)
    # now you can use that object every where
    artist = network.get_artist(artist_name)
    return [(s.item.name, s.match) for s in artist.get_similar()]


