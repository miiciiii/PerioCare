from django.db import models

# Create your models here.

class CallLog(models.Model):
    """
    Model to store call logs.
    """
    call_id = models.AutoField(primary_key=True)
    caller_name = models.CharField(max_length=255)
    caller_number = models.CharField(max_length=20)
    call_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caller_name} - {self.call_time.strftime('%Y-%m-%d %H:%M:%S')}"


class Assessment(models.Model):
    """
    Model to store patient assessments.
    """
    concern = models.TextField()
    severity = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='Pending')

    call_log = models.OneToOneField(CallLog, on_delete=models.CASCADE, related_name='assessment')

    def __str__(self):
        return f"{self.call_log.caller_name} - {self.concern[:50]} - {self.status}"
    
class Conversation(models.Model):
    """
    Model to store conversation history.
    """
    call_log = models.ForeignKey(CallLog, on_delete=models.CASCADE, related_name='conversations')
    user_input = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation for {self.call_log.caller_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    

