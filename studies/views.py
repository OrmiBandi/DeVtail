from rest_framework.viewsets import ModelViewSet

from .models import Study
from .serializers import StudySerializer

class StudyViewSet(ModelViewSet):
    '''
    스터디 관련 API
    '''
    queryset = Study.objects.all()
    serializer_class = StudySerializer

    def list(self, request, *args, **kwargs):
        '''
        스터디 리스트 조회 API
        '''
        return super().list(request, *args, **kwargs)