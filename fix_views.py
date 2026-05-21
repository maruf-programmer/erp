#!/usr/bin/env python
import os

with open('pages/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_code = '''    submission_form = None
    submission = None
    allow_submit = False

    if is_student:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        allow_submit = submission is None or submission.status == Submission.Status.REJECTED
        submission_form = SubmissionForm(request.POST or None, request.FILES or None, instance=submission if allow_submit else None)

        if request.method == 'POST' and submission_form.is_valid():
            if allow_submit:
                submission = submission_form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.status = Submission.Status.PENDING
                submission.score = None
                submission.silver_coins = 0
                submission.feedback = ''
                submission.reviewed_by = None
                submission.reviewed_at = None
                submission.teacher_seen_at = None
                submission.student_seen_review_at = None
                submission.submitted_at = timezone.now()
                submission.save()
                messages.success(request, 'Ishingiz tizimga yuklandi.')
                return redirect('assignment_detail', pk=assignment.pk)
            else:
                messages.error(request, "Sizda qayta topshirish huquqi yo'q. Oqituvchi ruxsat berganida qayta topshira olasiz.")
                return redirect('assignment_detail', pk=assignment.pk)

        if submission and submission.status != Submission.Status.PENDING and not submission.student_seen_review_at:
            submission.student_seen_review_at = timezone.now()
            submission.save(update_fields=['student_seen_review_at'])

        submissions = assignment.submissions.none()
    else:
        submissions = assignment.submissions.select_related('student').filter(Q(text__gt='') | Q(file__gt='')).annotate(
            late_order=Case(
                When(submitted_at__gt=assignment.deadline, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by('late_order', '-submitted_at')
        submissions.filter(status=Submission.Status.PENDING, teacher_seen_at__isnull=True).update(teacher_seen_at=timezone.now())

    return render(request, 'academy/assignment_detail.html', {
        'assignment': assignment,
        'submission_form': submission_form,
        'submission': submission,
        'submissions': submissions,
        'allow_submit': allow_submit,
        'is_student': is_student,
    })'''

start_marker = "    submission_form = None\n    submission = None\n    allow_submit = False"
end_marker = "    })\n\n\n@login_required\ndef grade_submission"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_code + "\n" + content[end_idx:]
    with open('pages/views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ Fixed string escaping in assignment_detail function body")
else:
    print("✗ Could not find markers")

