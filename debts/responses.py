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
