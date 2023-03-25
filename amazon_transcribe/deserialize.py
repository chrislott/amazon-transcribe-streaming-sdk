# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import json
from typing import Optional, Type, Any, List, Dict

import amazon_transcribe.exceptions as transcribe_exceptions
from amazon_transcribe.eventstream import BaseEvent
from amazon_transcribe.model import (
    StartStreamTranscriptionResponse,
    TranscriptResultStream,
    TranscriptEvent,
    Transcript,
    Result,
    Alternative,
    Item,
    Entity,
    StartCallAnalyticsStreamTranscriptionResponse,
    UtteranceEvent,
    CategoryEvent,
    CallAnalyticsItem,
    CallAnalyticsEntity,
    IssueDetected,
    CharacterOffsets,
    PointsOfInterest,
    TimestampRange,
    LanguageWithScore,
)
from amazon_transcribe.response import Response
from amazon_transcribe.exceptions import (
    ServiceException,
    BadRequestException,
    ConflictException,
    InternalFailureException,
    LimitExceededException,
    ServiceUnavailableException,
    UnknownServiceException,
    SerializationException,
)
from amazon_transcribe.utils import ensure_boolean


class TranscribeStreamingResponseParser:
    """Converts raw HTTP responses into modeled objects and exceptions.

    This class is not public and must not be consumed outside of this project.
    """

    def _get_error_code(self, http_response: Response) -> str:
        error_code = "Unknown"
        if "x-amzn-errortype" in http_response.headers:
            error_code = http_response.headers["x-amzn-errortype"]
            # Could be x-amzn-errortype: ValidationException:
            error_code = error_code.split(":")[0]
        return error_code

    def _get_error_message(self, body_bytes: bytes) -> str:
        error_message = "An unknown error was returned by the service"
        try:
            parsed_body = json.loads(body_bytes)
        except json.decoder.JSONDecodeError:
            return error_message
        if "Message" in parsed_body:
            error_message = parsed_body["Message"]
        elif "message" in parsed_body:
            error_message = parsed_body["message"]
        return error_message

    def parse_exception(
        self, http_response: Response, body_bytes: bytes
    ) -> ServiceException:
        error_code = self._get_error_code(http_response)
        error_message = self._get_error_message(body_bytes)
        if error_code == "BadRequestException":
            return BadRequestException(error_message)
        elif error_code == "ConflictException":
            return ConflictException(error_message)
        elif error_code == "InternalFailureException":
            return InternalFailureException(error_message)
        elif error_code == "LimitExceededException":
            return LimitExceededException(error_message)
        elif error_code == "ServiceUnavailableException":
            return ServiceUnavailableException(error_message)
        elif error_code == "SerializationException":
            return SerializationException(error_message)
        return UnknownServiceException(
            http_response.status_code,
            error_code,
            error_message,
        )

    def parse_start_stream_transcription_response(
        self,
        http_response: Response,
        body_stream: Any,
    ) -> StartStreamTranscriptionResponse:
        headers = http_response.headers
        request_id = headers.get("x-amzn-request-id")
        language_code = headers.get("x-amzn-transcribe-language-code")
        media_encoding = headers.get("x-amzn-transcribe-media-encoding")
        vocabulary_name = headers.get("x-amzn-transcribe-vocabulary-name")
        session_id = headers.get("x-amzn-transcribe-session-id")
        vocab_filter_name = headers.get("x-amzn-transcribe-vocabulary-filter-name")
        vocab_filter_method = headers.get("x-amzn-transcribe-vocabulary-filter-method")
        show_speaker_label = self._raw_value_to_bool(
            headers.get("x-amzn-transcribe-show-speaker-label")
        )
        enable_channel_identification = self._raw_value_to_bool(
            headers.get("x-amzn-transcribe-enable-channel-identification")
        )
        number_of_channels = self._raw_value_to_int(
            headers.get("x-amzn-transcribe-number-of-channels")
        )
        media_sample_rate_hz = self._raw_value_to_int(
            headers.get("x-amzn-transcribe-sample-rate")
        )
        enable_partial_results_stabilization = self._raw_value_to_bool(
            headers.get("x-amzn-transcribe-enable-partial-results-stabilization")
        )
        partial_results_stability = headers.get(
            "x-amzn-transcribe-partial-results-stability"
        )
        language_model_name = headers.get("x-amzn-transcribe-language-model-name")

        transcript_result_stream = TranscriptResultStream(
            body_stream, TranscribeStreamingEventParser()
        )

        parsed_response = StartStreamTranscriptionResponse(
            transcript_result_stream=transcript_result_stream,
            request_id=request_id,
            language_code=language_code,
            media_sample_rate_hz=media_sample_rate_hz,
            media_encoding=media_encoding,
            vocabulary_name=vocabulary_name,
            session_id=session_id,
            vocab_filter_name=vocab_filter_name,
            vocab_filter_method=vocab_filter_method,
            show_speaker_label=show_speaker_label,
            enable_channel_identification=enable_channel_identification,
            number_of_channels=number_of_channels,
            enable_partial_results_stabilization=enable_partial_results_stabilization,
            partial_results_stability=partial_results_stability,
            language_model_name=language_model_name,
        )
        return parsed_response

    def parse_start_call_analytics_stream_transcription_response(
        self,
        http_response: Response,
        body_stream: Any,
    ) -> StartCallAnalyticsStreamTranscriptionResponse:
        headers = http_response.headers
        request_id = headers.get("x-amzn-request-id")
        language_code = headers.get("x-amzn-transcribe-language-code")
        media_encoding = headers.get("x-amzn-transcribe-media-encoding")
        vocabulary_name = headers.get("x-amzn-transcribe-vocabulary-name")
        session_id = headers.get("x-amzn-transcribe-session-id")
        vocab_filter_name = headers.get("x-amzn-transcribe-vocabulary-filter-name")
        vocab_filter_method = headers.get("x-amzn-transcribe-vocabulary-filter-method")

        media_sample_rate_hz = self._raw_value_to_int(headers.get("x-amzn-transcribe-sample-rate"))
        enable_partial_results_stabilization = self._raw_value_to_bool(
            headers.get("x-amzn-transcribe-enable-partial-results-stabilization")
        )
        partial_results_stability = headers.get("x-amzn-transcribe-partial-results-stability")
        language_model_name = headers.get("x-amzn-transcribe-language-model-name")

        content_identification_type = headers.get("x-amzn-transcribe-content-identification-type")
        content_redaction_type = headers.get("x-amzn-transcribe-content-redaction-type")
        pii_entity_types = headers.get("x-amzn-transcribe-pii-entity-types")

        transcript_result_stream = TranscriptResultStream(
            body_stream, TranscribeStreamingEventParser()
        )

        parsed_response = StartCallAnalyticsStreamTranscriptionResponse(
            transcript_result_stream=transcript_result_stream,
            request_id=request_id,
            language_code=language_code,
            media_sample_rate_hz=media_sample_rate_hz,
            media_encoding=media_encoding,
            vocabulary_name=vocabulary_name,
            session_id=session_id,
            vocab_filter_name=vocab_filter_name,
            vocab_filter_method=vocab_filter_method,
            language_model_name=language_model_name,
            enable_partial_results_stabilization=enable_partial_results_stabilization,
            partial_results_stability=partial_results_stability,
            content_identification_type=content_identification_type,
            content_redaction_type=content_redaction_type,
            pii_entity_types=pii_entity_types,
        )
        return parsed_response

    def _raw_value_to_int(self, value: Optional[str]) -> Optional[int]:
        if value:
            return int(value)
        return None

    def _raw_value_to_bool(self, value: Optional[str]) -> Optional[bool]:
        if value is not None:
            return ensure_boolean(value)
        return None


class TranscribeStreamingEventParser:
    def parse(self, raw_event) -> Optional[BaseEvent]:
        message_type = raw_event.headers.get(":message-type")
        if message_type in ["error", "exception"]:
            raise self._parse_event_exception(raw_event)
        elif message_type == "event":
            event_type = raw_event.headers.get(":event-type")
            raw_body = json.loads(raw_event.payload)
            if event_type == "TranscriptEvent":
                # TODO: Handle cases where the service returns an incorrect response
                return self._parse_transcript_event(raw_body)
            if event_type == "UtteranceEvent":
                # TODO: Handle cases where the service returns an incorrect response
                return self._parse_utterance_event(raw_body)
            if event_type == "CategoryEvent":
                # TODO: Handle cases where the service returns an incorrect response
                return self._parse_category_event(raw_body)
        return None

    def _parse_transcript_event(self, current_node: Any) -> TranscriptEvent:
        transcript = self._parse_transcript(current_node.get("Transcript"))
        return TranscriptEvent(transcript)

    def _parse_utterance_event(self, current_node: Any) -> UtteranceEvent:
        utterance_id = current_node.get("UtteranceId")
        is_partial = current_node.get("IsPartial")
        participant_role = current_node.get("ParticipantRole")
        begin_offset_millis = current_node.get("BeginOffsetMillis")
        end_offset_millis = current_node.get("EndOffsetMillis")
        transcript = current_node.get("Transcript")
        items = self._parse_call_analytics_item_list(current_node.get("Items"))
        entities = self._parse_call_analytics_entity_list(current_node.get("Entities"))
        sentiment = current_node.get("Sentiment")
        issues_detected = self._parse_issues_detected_list(current_node.get("IssuesDetected"))

        return UtteranceEvent(
            utterance_id,
            is_partial,
            participant_role,
            begin_offset_millis,
            end_offset_millis,
            transcript,
            items,
            entities,
            sentiment,
            issues_detected,
        )

    def _parse_call_analytics_item_list(
        self, current_node: Any
    ) -> Optional[List[CallAnalyticsItem]]:
        if current_node is None:
            return None
        return [self._parse_call_analytics_item(e) for e in current_node]

    def _parse_call_analytics_entity_list(
        self, current_node: Any
    ) -> Optional[List[CallAnalyticsEntity]]:
        if current_node is None:
            return None
        return [self._parse_call_analytics_entity(e) for e in current_node]

    def _parse_issues_detected_list(self, current_node: Any) -> Optional[List[IssueDetected]]:
        if current_node is None:
            return None
        return [self._parse_issue_detected(e) for e in current_node]

    def _parse_issue_detected(self, current_node: Any) -> IssueDetected:
        character_offsets = self._parse_character_offsets(current_node.get("CharacterOffsets"))
        return IssueDetected(character_offsets)

    def _parse_character_offsets(self, current_node: Any) -> CharacterOffsets:
        begin = current_node.get("Begin")
        end = current_node.get("End")
        return CharacterOffsets(begin, end)

    def _parse_call_analytics_entity(self, current_node: Any) -> CallAnalyticsEntity:
        begin_offset_millis = current_node.get("BeginOffsetMillis")
        end_offset_millis = current_node.get("EndOffsetMillis")
        category = current_node.get("Category")
        entity_type = current_node.get("Type")
        content = current_node.get("Content")
        confidence = current_node.get("Confidence")
        return CallAnalyticsEntity(
            begin_offset_millis,
            end_offset_millis,
            category,
            entity_type,
            content,
            confidence,
        )

    def _parse_call_analytics_item(self, current_node: Any) -> CallAnalyticsItem:
        begin_offset_millis = current_node.get("BeginOffsetMillis")
        end_offset_millis = current_node.get("EndOffsetMillis")
        item_type = current_node.get("Type")
        content = current_node.get("Content")
        confidence = current_node.get("Confidence")
        vocabulary_filter_match = current_node.get("VocabularyFilterMatch")
        stable = current_node.get("Stable")
        return CallAnalyticsItem(
            begin_offset_millis,
            end_offset_millis,
            item_type,
            content,
            confidence,
            vocabulary_filter_match,
            stable,
        )

    def _parse_category_event(self, current_node: Any) -> CategoryEvent:
        matched_categories = self._parse_matched_categories_list(
            current_node.get("MatchedCategories")
        )
        matched_details = self._parse_matched_details_dict(current_node.get("MatchedDetails"))
        return CategoryEvent(matched_categories, matched_details)

    def _parse_matched_categories_list(self, current_node: Any) -> List[str]:
        return [self._parse_category(e) for e in current_node]

    def _parse_matched_details_dict(self, current_node: Any) -> Dict[str, PointsOfInterest]:
        matched_details = {}
        for key, value in current_node.items():
            matched_details[key] = self._parse_points_of_interest(value)
        return matched_details
        # return [self._parse_points_of_interest_dict(e) for e in current_node]

    def _parse_points_of_interest(self, current_node: Any) -> PointsOfInterest:
        timestamp_ranges = self._parse_timestamp_ranges(current_node.get("TimestampRanges"))
        return PointsOfInterest(timestamp_ranges)

    def _parse_timestamp_ranges(self, current_node: Any) -> List[TimestampRange]:
        return [self._parse_timestamp_range(e) for e in current_node]

    def _parse_timestamp_range(self, current_node: Any) -> TimestampRange:
        begin_offset_millis = current_node.get("BeginOffsetMillis")
        end_offset_millis = current_node.get("EndOffsetMillis")
        return TimestampRange(begin_offset_millis, end_offset_millis)

    def _parse_category(self, current_node: Any) -> str:
        return current_node

    def _parse_transcript(self, current_node: Any) -> Transcript:
        results = self._parse_result_list(current_node.get("Results"))
        return Transcript(results)

    def _parse_result_list(self, current_node: Any) -> List[Result]:
        return [self._parse_result(e) for e in current_node]

    def _parse_result(self, current_node: Any) -> Result:
        alternatives = self._parse_alternative_list(current_node.get("Alternatives"))
        language_identification = self._parse_language_identification_list(
            current_node.get("LanguageIdentification")
        )

        return Result(
            result_id=current_node.get("ResultId"),
            start_time=current_node.get("StartTime"),
            end_time=current_node.get("EndTime"),
            is_partial=current_node.get("IsPartial"),
            alternatives=alternatives,
            channel_id=current_node.get("ChannelId"),
            language_identification=language_identification,
        )

    def _parse_alternative_list(self, current_node: Any) -> List[Alternative]:
        if current_node is None:
            return None
        return [self._parse_alternative(e) for e in current_node]

    def _parse_language_identification_list(self, current_node: Any) -> List[LanguageWithScore]:
        if current_node is None:
            return None
        return [self._parse_language_with_score(e) for e in current_node]

    def _parse_language_with_score(self, current_node: Any) -> LanguageWithScore:
        if current_node is None:
            return None
        return LanguageWithScore(
            language_code=current_node.get("LanguageCode"),
            score=current_node.get("Score"),
        )

    def _parse_alternative(self, current_node: Any) -> Alternative:
        return Alternative(
            transcript=current_node.get("Transcript"),
            items=self._parse_item_list(current_node.get("Items")),
            entities=self._parse_entity_list(current_node.get("Entities")),
        )

    def _parse_entity_list(self, current_node: Any) -> List[Entity]:
        if current_node is None:
            return None
        return [self._parse_entity(e) for e in current_node]

    def _parse_item_list(self, current_node: Any) -> List[Item]:
        return [self._parse_item(e) for e in current_node]

    def _parse_item(self, current_node: Any) -> Item:
        return Item(
            start_time=current_node.get("StartTime"),
            end_time=current_node.get("EndTime"),
            item_type=current_node.get("Type"),
            content=current_node.get("Content"),
            vocabulary_filter_match=current_node.get("VocabularyFilterMatch"),
            speaker=current_node.get("Speaker"),
            confidence=current_node.get("Confidence"),
            stable=current_node.get("Stable"),
        )

    def _parse_entity(self, current_node: Any) -> Entity:
        return Entity(
            start_time=current_node.get("StartTime"),
            end_time=current_node.get("EndTime"),
            category=current_node.get("Category"),
            type=current_node.get("Type"),
            content=current_node.get("Content"),
            confidence=current_node.get("Confidence"),
        )

    def _parse_event_exception(self, raw_event) -> ServiceException:
        exception_type: str = raw_event.headers.get(
            ":exception-type", "ServiceException"
        )
        exception_cls: Type[ServiceException] = getattr(
            transcribe_exceptions, exception_type, ServiceException
        )
        try:
            raw_body = json.loads(raw_event.payload)
        except ValueError:
            raw_body = {}
        exception_msg = raw_body.get("Message", "An unknown service exception occured")
        return exception_cls(exception_msg)
