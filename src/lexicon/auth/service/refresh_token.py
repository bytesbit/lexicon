from rest_framework_simplejwt.tokens import RefreshToken


def get_access_token_from_refresh_token(refresh_token):
    """
    Returns new access_token for the refresh token
    :param refresh_token:
    :return access_token, refresh_token and their expiry time:
    """

    refresh = RefreshToken(token=refresh_token)
    data = {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "refresh_exp_at": refresh["exp"],
        "access_exp_at": refresh.access_token["exp"],
    }
    return data
