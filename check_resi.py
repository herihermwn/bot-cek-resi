import json
import requests


def check_resi(expedition, resi):
    url = "https://pluginongkoskirim.com/cek-tarif-ongkir/front/resi-amp"
    data = {"kurir": expedition, "resi": resi}
    try:
        response = requests.post(url, data=data)
        result = json.loads(response.text)
        return result
    except Exception as e:
        return {
            "error": True, 
            "message": "{}".format(e)
        }
