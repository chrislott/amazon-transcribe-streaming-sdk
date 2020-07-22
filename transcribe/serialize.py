from io import BufferedIOBase, BytesIO
from typing import Dict, List, Tuple, Union

from transcribe.model import AudioEvent, StartStreamTranscriptionRequest
from transcribe.exceptions import ValidationException
from transcribe.request import PreparedRequest, Request
from transcribe.structures import BufferableByteStream
from transcribe.utils import _add_required_headers

REQUEST_TYPE = Union[Request, PreparedRequest]
HEADER_VALUE = Union[int, None, str]


class Serializer:
    def __init__(self):
        raise NotImplementedError("Serializer")

    def serialize(self) -> Tuple[Dict[str, HEADER_VALUE], BufferedIOBase]:
        """Serialize out to payload and headers."""
        raise NotImplementedError("serialize")

    def serialize_to_request(self, prepare=True) -> REQUEST_TYPE:
        """Serialize parameters into an HTTP request."""
        raise NotImplementedError("serialize_to_request")


class TranscribeStreamingRequestSerializer(Serializer):
    """Convert StartStreamTranscriptionRequest into a
    Request object for streaming to the Transcribe service.
    """

    def __init__(self, endpoint, transcribe_request):
        self.endpoint: str = endpoint
        self.method: str = "POST"
        self.request_uri: str = "/stream-transcription"
        self.request_shape: StartStreamTranscriptionRequest = transcribe_request

    def serialize(self) -> Tuple[Dict[str, HEADER_VALUE], BufferedIOBase]:
        headers = {
            "x-amzn-transcribe-language-code": self.request_shape.language_code,
            "x-amzn-transcribe-sample-rate": self.request_shape.media_sample_rate_hz,
            "x-amzn-transcribe-media-encoding": self.request_shape.media_encoding,
            "x-amzn-transcribe-vocabulary-name": self.request_shape.vocabulary_name,
            "x-amzn-transcribe-session-id": self.request_shape.session_id,
            "x-amzn-transcribe-vocabulary-filter-method": self.request_shape.vocab_filter_method,
        }
        _add_required_headers(self.endpoint, headers)

        body = BufferableByteStream()
        return headers, body

    def serialize_to_request(self, prepare=True) -> REQUEST_TYPE:
        headers, body = self.serialize()
        request = Request(
            endpoint=self.endpoint,
            path=self.request_uri,
            method=self.method,
            headers=headers,
            body=body,
        )
        if prepare:
            return request.prepare()
        return request


class AudioEventSerializer:
    """Convert AudioEvent objects into payload and header outputs for eventstreams"""

    def serialize(
        self, audio_event: AudioEvent
    ) -> Tuple[Dict[str, str], bytes]:
        headers = {
            ":message-type": "event",
            ":event-type": "AudioEvent",
            ":content-type": "application/octet-stream",
        }
        return headers, audio_event.payload
