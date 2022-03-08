from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room, Message
from .serializers import RoomSerializer, MessageSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id',
        'GET /api/messages',
        'GET/api/messages/:user',
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serialized = RoomSerializer(rooms, many=True)
    return Response(serialized.data)

@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serialized = RoomSerializer(room, many=False)
    return Response(serialized.data)

@api_view(['GET'])
def getMessages(request):
    messages = Message.objects.all()
    serialized = MessageSerializer(messages, many=True)
    return Response(serialized.data)

@api_view(['GET'])
def getMessagesByUser(request, pk):
    messages = Message.objects.filter(user_id=pk)
    serialized = MessageSerializer(messages, many=True)
    return Response(serialized.data)