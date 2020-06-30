from requests import get


def analytic_data(key, **kwargs):
    """
    Get analytic data from RescueTime

    https://www.rescuetime.com/anapi/setup/documentation#analytic-api-reference
    """
    res = get('https://www.rescuetime.com/anapi/data', {
        'key': key,
        'format': 'json',
        **kwargs,
    })
    if 'format' in kwargs and kwargs['format'] == 'csv':
        return res.text
    else:
        res.json()
