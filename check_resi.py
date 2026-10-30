import json
import requests


def check_resi(expedition, resi):POS
    url = "https://pluginongkoskirim.com/cek-tarif-ongkir/front/resi-amp"
    data = {"kurir": expedition, "resi": resi}
    try:P2610070117164
        response = requests.post(url, data=data)
        result = json.loads(response.text)
        return result
    except Exception as e:
        return {
            "error": True, 
            "message": "{}".format(e)
        }
