from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import DirectChat
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def create_or_connect_direct_chat(request):
    # 대화 상대의 ID를 GET 매개변수로 가져옴
    target_user_id = request.POST.get("target_user_id")

    # 대화 상대의 ID가 없으면 에러 응답
    if not target_user_id:
        return JsonResponse({"error": "Target user ID is required."}, status=400)

    # 현재 로그인한 사용자와 대화 상대의 ID를 가져옴
    current_user_id = request.user.id
    target_user = get_object_or_404(User, id=target_user_id)

    # 이미 생성된 채팅방이 있는지 확인
    existing_chat = (
        DirectChat.objects.filter(users=current_user_id)
        .filter(users=target_user_id)
        .first()
    )

    if existing_chat:
        # 이미 존재하는 채팅방에 연결
        room_id = existing_chat.id
    else:
        # 채팅방이 없으면 생성 후 연결
        new_chat = DirectChat.objects.create()
        new_chat.users.add(current_user_id, target_user_id)
        room_id = new_chat.id

    # 생성된 채팅방으로 리다이렉트
    if room_id:
        return render(request, "chats/temp_direct_chat.html", {"room_id": room_id})
    # 우선 JsonResponse로 에러 처리 (추후 리다이렉트로 변경)
    return JsonResponse({"error": "Invalid room ID."}, status=400)
