from helpers import img_from_url


class UserProfile:
    def __init__(self, profile):
        self.username = profile.get('username', '')
        self.full_name = profile.get('full_name', '')
        self.follower_count = profile.get('edge_followed_by', {}).get('count', 0)
        self.following_count = profile.get('edge_follow', {}).get('count', 0)
        self.biography = profile.get('biography', '')
        self.id = profile.get('id', '')
        self.profile_pic_url = profile.get('profile_pic_url', '')
        self.profile_pic_url_hd = profile.get('profile_pic_url_hd', '')
        self.profile_pic = img_from_url(self.profile_pic_url)
