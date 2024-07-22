from django.urls import path
from .views import SetupSDK, StreamConversation,UploadAudioFormView,TranscribeAudioView

urlpatterns = [
    path('setup/', SetupSDK.as_view(), name='setup-sdk'),
    path('upload/', UploadAudioFormView.as_view(), name='upload_audio_form'),
    path('stream/', StreamConversation.as_view(), name='stream-conversation'),
    path('transcribe/',TranscribeAudioView.as_view(),name='transcribe'),
]
