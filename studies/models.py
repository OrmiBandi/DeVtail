from django.db import models


class Study(models.Model):
    """
    스터디 모델
    """

    difficulty_choices = [
        ("상", "상"),
        ("중", "중"),
        ("하", "하"),
    ]
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT, related_name="studies"
    )
    goal = models.CharField(max_length=100)
    thumbnail = models.ImageField(
        upload_to="study/imgs/%Y/%m/%d/", null=True, blank=True
    )
    start_at = models.DateField()
    end_at = models.DateField()
    introduce = models.TextField(null=True, blank=True)
    topic = models.CharField(max_length=100, null=True, blank=True)
    difficulty = models.CharField(max_length=2, choices=difficulty_choices)
    current_member = models.IntegerField(default=0)
    max_member = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "스터디"
        verbose_name_plural = "스터디"

    def __str__(self):
        return f"스터디 목표 : {self.study_goal}"


class Schedule(models.Model):
    """
    스터디 일정 모델
    """

    day_choices = [
        (1, "월요일"),
        (2, "화요일"),
        (3, "수요일"),
        (4, "목요일"),
        (5, "금요일"),
        (6, "토요일"),
        (7, "일요일"),
    ]
    study = models.ForeignKey(
        "Study", on_delete=models.CASCADE, related_name="schedules"
    )
    day = models.IntegerField(choices=day_choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name = "스터디 일정"
        verbose_name_plural = "스터디 일정"

    def __str__(self):
        return f"스터디 : {self.study}, 요일 : {self.day}"


class Category(models.Model):
    """
    카테고리 모델
     - 스터디의 카테고리를 설정
     - 운영진이 카테고리를 생성, 저장하고 목록을 제공하는 방식
    """

    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    태그 모델
     - 스터디의 태그 설정
     - 스터디 생성 시 사용자가 입력한 태그를 저장
    """

    study = models.ForeignKey("Study", on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그"

    def __str__(self):
        return self.name


class RefLink(models.Model):
    """
    참조링크 모델
     - 스터디의 참조 링크 저장
     - category의 경우 GitHub, Notion과 같은 링크 타입을 설명
    """

    study = models.ForeignKey(
        "Study", on_delete=models.CASCADE, related_name="ref_links"
    )
    link_type = models.CharField(max_length=100)
    url = models.CharField(max_length=100)

    class Meta:
        verbose_name = "참조링크"
        verbose_name_plural = "참조링크"

    def __str__(self):
        return f"스터디 : {self.study}, 링크 타입 : {self.link_type}"


class Comment(models.Model):
    """
    댓글 모델
     - 스터디 모집글, 내용 등에 댓글 노출
    """

    study = models.ForeignKey(
        "Study", on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, related_name="comments", null=True
    )
    content = models.TextField()
    is_secret = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "댓글"
        verbose_name_plural = "댓글"

    def __str__(self):
        return f"스터디 : {self.study}, 작성자 : {self.user.username}"


class Recomment(models.Model):
    """
    대대댓글 모델
     - 댓글에 대한 대댓글
    """

    comment = models.ForeignKey(
        "Comment", on_delete=models.CASCADE, related_name="recomments"
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, related_name="recomments", null=True
    )
    content = models.TextField()
    is_secret = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "대댓글"
        verbose_name_plural = "대댓글"

    def __str__(self):
        return f"댓글 : {self.comment}, 작성자 : {self.user.username}"


class StudyMember(models.Model):
    """
    스터디 멤버 모델
    """

    study = models.ForeignKey("Study", on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="studies"
    )
    is_accepted = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    class Meta:
        verbose_name = "스터디 멤버"
        verbose_name_plural = "스터디 멤버"

    def __str__(self):
        return f"스터디 : {self.study}, 회원 : {self.user.username}"


class Blacklist(models.Model):
    """
    스터디 블랙리스트 모델
    """

    study = models.ForeignKey(
        "Study", on_delete=models.CASCADE, related_name="blacklists"
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="blacklists"
    )

    class Meta:
        verbose_name = "스터디 블랙리스트"
        verbose_name_plural = "스터디 블랙리스트"

    def __str__(self):
        return f"스터디 : {self.study}, 회원 : {self.user.username}"


class Favorite(models.Model):
    """
    스터디 즐겨찾기 모델
    """

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="favorites"
    )
    study = models.ForeignKey(
        "Study", on_delete=models.SET_NULL, null=True, related_name="favorites"
    )

    class Meta:
        verbose_name = "스터디 즐겨찾기"
        verbose_name_plural = "스터디 즐겨찾기"

    def __str__(self):
        return f"스터디 즐겨찾기 : {self.study}, 회원 : {self.user.username}"
