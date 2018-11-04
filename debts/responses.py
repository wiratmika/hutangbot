from django.utils import timezone


def GenericSuccessResponse(content):
    return {
        'response_type': 'ephemeral',
        'attachments': [{
            'text': content,
            'color': 'good',
            'ts': timezone.now().timestamp()
        }]
    }


def AttachmentSuccessResponse(content_tuples, caption=None):
    response = {
        'response_type': 'ephemeral',
        'attachments': [{
            'fields': [{
                'title': content[0],
                'value': content[1],
                'short': content[2]
            } for content in content_tuples],
            'color': 'good',
            'ts': timezone.now().timestamp()
        }]
    }

    if caption:
        response['text'] = caption

    return response
