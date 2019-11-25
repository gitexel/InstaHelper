from requests import Response

from settings import APIBackendData, UserData
import requests as req


class BackendService:
    def __init__(self):
        self.user_data = UserData()
        self.api_data = APIBackendData()

    def get_headers(self, refreshed_settings=False):
        return {'Authorization': 'Token %s' % self.user_data.get_subscription_key(refresh_settings=refreshed_settings)}

    def subscription_status(self):
        """

        :return:
        {'valid': True, 'end_date': date}
        """
        result: Response = req.get(url=self.api_data.api_url + 'service/%s/status' % self.user_data.username,
                                   headers=self.get_headers(refreshed_settings=True)).json()
        print(self.get_headers(refreshed_settings=True))
        return result
        # raise Exception("backend error")  # todo handel error

    #
    # def have_unfollow_task(self):
    #     result = req.get(url=self.API_URL + '%s/situation?format=json' % self.username, headers=self.headers).json()
    #     if result:
    #         try:
    #             return result['unfollowing']
    #         except KeyError:
    #             return False
    #     else:
    #         return False
    #
    # def follow_task(self, user_id):
    #
    #     try:
    #
    #         response = self.app.insta.friendships_create(user_id)
    #         Logger.debug(str(response))
    #     except errors.ClientBadRequestError as er:
    #         Logger.info(er)
    #         self.set_challenge(True)
    #         return False
    #
    #     if response['status'] == 'ok':
    #
    #         Logger.info('%s followed %s' % (self.username, user_id))
    #
    #         status = self.update_followed_to_backend(user_id)
    #
    #         if status != 200:
    #             Logger.warning(
    #                 'followed: failed to update %s to the server, status: %s' % (user_id, status))
    #
    #     else:
    #         Logger.warning('%s failed to follow %s: Instagram error' % (self.username, user_id))
    #         Logger.debug('%s failed to follow %s: Instagram error' % (self.username, user_id))
    #         return False
    #
    #     return True
    #
    # def unfollow_task(self, user_id):
    #     try:
    #         response = self.app.insta.friendships_destroy(user_id)
    #         Logger.debug(str(response))
    #     except errors.ClientBadRequestError as er:
    #         Logger.info(er)
    #         self.set_challenge(True)
    #         return False
    #
    #     if response['status'] == 'ok':
    #
    #         Logger.info('%s unfollowed %s' % (self.username, user_id))
    #
    #         status = self.update_unfollowed_to_backend(user_id)
    #
    #         if status != 200:
    #             Logger.warning(
    #                 'unfollowed: failed to update %s to the server, status: %s' % (user_id, status))
    #
    #     else:
    #
    #         Logger.warning('%s failed to unfollow %s: instagram error' % (self.username, user_id))
    #
    #         status = self.update_unfollowed_to_backend(user_id=user_id, done=False, valid=False)
    #
    #         if status != 200:
    #             Logger.warning(
    #                 'unfollowed: failed to update %s to the server, status: %s' % (user_id, status))
    #         return False
    #
    #     return True
    #
    # def get_users_for_follow(self):
    #     result = req.get(url=self.API_URL + '%s/products/to_follow?format=json' % self.username, headers=self.headers).json()
    #     try:
    #         result['ids']
    #     except KeyError:
    #         return []
    #     return result['ids']
    #
    # def get_users_for_unfollow(self):
    #
    #     result = req.get(url=self.API_URL + '%s/products/to_unfollow?format=json' % self.username,
    #                      headers=self.headers).json()
    #     try:
    #         result['ids']
    #     except KeyError:
    #         return []
    #     return result['ids']
    #
    # def update_followed_to_backend(self, user_id, done=True, valid=True):
    #     if done and valid:
    #         dic = {'followed': done, 'valid': valid}
    #     else:
    #         dic = {'followed': done, 'valid': valid}
    #     return req.put(url=self.API_URL + '%s/products/followed/%s' % (self.username, user_id), headers=self.headers,
    #                    json=dic).status_code
    #
    # def update_unfollowed_to_backend(self, user_id, done=True, valid=True):
    #     if done and valid:
    #         dic = {'unfollowed': done, 'valid': valid}
    #     else:
    #         dic = {'unfollowed': done, 'valid': valid}
    #
    #     return req.put(url=self.API_URL + '%s/products/unfollowed/%s' % (self.username, user_id), headers=self.headers
    #                    , json=dic).status_code
    #
    # def update_user_status_to_backend(self):
    #
    #     profile = self.app.insta.user_info2(self.username)
    #
    #     following = profile['counts']['follows']
    #     followers = profile['counts']['followed_by']
    #
    #     dic = {'followers': followers, 'following': following}
    #
    #     return req.put(url=self.API_URL + 'subscriptions/update/%s/' % self.subscription_id, headers=self.headers,
    #                    json=dic).status_code
