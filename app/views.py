from django.http import JsonResponse
import warnings
from PIL import Image
from io import BytesIO
import json
import base64
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from django.views.decorators.csrf import csrf_exempt
import re
from django.shortcuts import render


def index(request, template="index.html", ):
    return render(request, template, {})


@csrf_exempt
def sdk_gen(request):
    body = json.loads(request.body)
    image_data = re.sub('^data:image/.+;base64,', '', body['start_img'])
    im = Image.open(BytesIO(base64.b64decode(image_data)))
    im = im.resize((768, 512))
    stability_api = client.StabilityInference(
        key="sk-KdPQlYdDb3dw22xawhlZvWX37fV6sCCb7Oo803WbsQgO3Wri",
        verbose=True,
    )

    answers = stability_api.generate(
        prompt=body["input"],
        seed="",  # if provided, specifying a random seed makes results deterministic
        steps=100,  # defaults to 50 if not specified
        init_image=im
    )

# iterating over the generator produces the api response
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                return warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                store = artifact.binary
                img = str(base64.b64encode(store))
                return JsonResponse({'img': img[2:-1]})
