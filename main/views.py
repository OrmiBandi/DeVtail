import holidays
import datetime

from django.shortcuts import render

from studies.models import Study, StudyMember


def index(request):
    """
    메인 화면 렌더링 함수
        - 가장 가까운 공휴일 3개의 정보를 담아서 client에게 전달
            - 공휴일 중 대체공휴일은 제외
        - 스터디 데이터 8개를 담아서 client에게 전달
            - 최근 스터디 순으로 정렬하여 전달
        - 로그인된 유저의 경우, 유저가 참여중인 스터디 데이터 4개를 담아서 client에게 전달
            - 최근 스터디 순으로 정렬하여 전달
    """
    context = {"holidays": []}
    today = datetime.date.today()
    kr_holidays = dict(holidays.KR(years=today.year, language="ko"))
    filtered_holidays = list(filter(lambda x: x > today, kr_holidays))
    filtered_holidays.sort()
    for i in range(len(filtered_holidays)):
        if "대체" in kr_holidays[filtered_holidays[i]]:
            filtered_holidays.pop(i)
            break
    for i in filtered_holidays[:3]:
        context["holidays"].append({"date": i, "name": kr_holidays[i]})

    studies = Study.objects.all().order_by("-created_at")[:8]

    for study in studies:
        study_members = StudyMember.objects.filter(study=study, is_accepted=True)
        study.memeber_count = study_members.count()
        study.manager = study_members.filter(is_manager=True).first().user

    context["studies"] = studies
    if request.user.is_authenticated:
        my_studies = Study.objects.filter(members__user=request.user).order_by(
            "-created_at"
        )[:4]
        for study in my_studies:
            study_members = StudyMember.objects.filter(study=study, is_accepted=True)
            study.memeber_count = study_members.count()
            study.manager = study_members.filter(is_manager=True).first().user

        context["my_studies"] = my_studies

    return render(request, "index.html", context=context)
