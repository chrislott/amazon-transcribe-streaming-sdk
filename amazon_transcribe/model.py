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

from typing import Optional, List, Dict

from amazon_transcribe.eventstream import BaseEvent, BaseStream, EventStream


class Alternative:
    """A list of possible transcriptions for the audio.

    :param transcript: The text that was transcribed from the audio.
    :param items: One or more alternative interpretations of the input audio.
    """

    def __init__(self, transcript, items, entities=None):
        self.transcript: str = transcript
        self.items: List[Item] = items
        self.entities: List[Entity] = entities


class AudioEvent(BaseEvent):
    """Provides a wrapper for the audio chunks that you are sending.

    :param audio_chunk:
        A blob of audio from your application. You audio stream consists
        of one or more audio events. The maximum audio chunk size is 32 KB.
    """

    def __init__(self, audio_chunk: Optional[bytes]):
        if audio_chunk is None:
            audio_chunk = b""
        super().__init__(payload=audio_chunk)

    @property
    def audio_chunk(self):
        return self.payload


class AudioStream(BaseStream):
    """Input audio stream for transcription stream request.

    This should never be instantiated by the end user. It will be returned
    from the client within a relevant wrapper object.
    """

    async def send_audio_event(self, audio_chunk: Optional[bytes]):
        """Enqueue audio bytes to be sent for transcription.

        :param audio_chunk: byte-string chunk of audio input.
            The maximum audio chunk size is 32 KB.
        """
        audio_event = AudioEvent(audio_chunk)
        await super().send_event(audio_event)

    async def send_configuration_event(self, configuration_event):
        """Enqueue audio bytes to be sent for transcription.

        :param audio_chunk: byte-string chunk of audio input.
            The maximum audio chunk size is 32 KB.
        """
        await super().send_event(configuration_event)


class Item:
    """A word, phrase, or punctuation mark that is transcribed from the input audio.

    :param start_time:
        The offset from the beginning of the audio stream to the beginning
        of the audio that resulted in the item.

    :param end_time:
        The offset from the beginning of the audio stream to the end of
        the audio that resulted in the item.

    :param item_type: The type of the item.

    :param content:
        The word or punctuation that was recognized in the input audio.

    :param vocabulary_filter_match:
        Indicates whether a word in the item matches a word in the vocabulary
        filter you've chosen for your real-time stream. If True then a word
        in the item matches your vocabulary filter.

    :param speaker:
        If speaker identification is enabled, shows the speakers identified
        in the real-time stream.

    :param confidence:
        A value between 0 and 1 for an item that is a confidence score that
        Amazon Transcribe assigns to each word or phrase that it transcribes.

    :param stable:
       If partial result stabilization has been enabled, indicates whether the
       word or phrase in the item is stable. If Stable is true,
       the result is stable.
    """

    def __init__(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        item_type: Optional[str] = None,
        content: Optional[str] = None,
        vocabulary_filter_match: Optional[bool] = None,
        speaker: Optional[str] = None,
        confidence: Optional[float] = None,
        stable: Optional[bool] = None,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.item_type = item_type
        self.content = content
        self.vocabulary_filter_match = vocabulary_filter_match
        self.speaker = speaker
        self.confidence = confidence
        self.stable = stable


class LanguageWithScore:
    """A list of possible transcriptions for the audio.

    :param LanguageCode:
        The language code of the identified language.

    :param Score:
        The confidence score associated with the identified language code.
        Confidence scores are values between zero and one; larger values
        indicate a higher confidence in the identified language.

    """

    def __init__(self, language_code: Optional[str] = None, score: Optional[float] = None):
        self.language_code = language_code
        self.score = score


class Result:
    """The result of transcribing a portion of the input audio stream.

    :param result_id: A unique identifier for the result.

    :param start_time:
        The offset in seconds from the beginning of the audio stream to the
        beginning of the result.

    :param end_time:
        The offset in seconds from the beginning of the audio stream to the
        end of the result.

    :param is_partial:
        Amazon Transcribe divides the incoming audio stream into segments at
        natural points in the audio. Transcription results are returned based
        on these segments. True indicates that Amazon Transcribe has additional
        transcription data to send, False to indicate that this is the last
        transcription result for the segment.

    :param alternatives:
        A list of possible transcriptions for the audio. Each alternative
        typically contains one Item that contains the result of the transcription.

    :param channel_id:
        When channel identification is enabled, Amazon Transcribe transcribes
        the speech from each audio channel separately. You can use ChannelId
        to retrieve the transcription results for a single channel in your
        audio stream.
    """

    def __init__(
        self,
        result_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        is_partial: Optional[bool] = None,
        alternatives: Optional[List[Alternative]] = None,
        channel_id: Optional[str] = None,
        language_code: Optional[str] = None,
        language_identification: Optional[List[LanguageWithScore]] = None,
    ):
        self.result_id = result_id
        self.start_time = start_time
        self.end_time = end_time
        self.is_partial = is_partial
        self.alternatives = alternatives
        self.channel_id = channel_id
        self.language_code = language_code
        self.language_identification = language_identification


class StartStreamTranscriptionRequest:
    """Transcription Request

    :param language_code:
        Indicates the source language used in the input audio stream.

    :param media_sample_rate_hz:
        The sample rate, in Hertz, of the input audio. We suggest that you
        use 8000 Hz for low quality audio and 16000 Hz for high quality audio.

    :param media_encoding:
        The encoding used for the input audio.

    :param vocabulary_name:
        The name of the vocabulary to use when processing the transcription job.

    :param session_id:
        A identifier for the transcription session. Use this parameter when you
        want to retry a session. If you don't provide a session ID,
        Amazon Transcribe will generate one for you and return it in the response.

    :param vocab_filter_method:
        The manner in which you use your vocabulary filter to filter words in
        your transcript.

    :param vocab_filter_name:
        The name of the vocabulary filter you've created that is unique to
        your AWS account. Provide the name in this field to successfully
        use it in a stream.

    :param show_speaker_label:
        When true, enables speaker identification in your real-time stream.

    :param enable_channel_identification:
        When true, instructs Amazon Transcribe to process each audio channel
        separately and then merge the transcription output of each channel
        into a single transcription. Amazon Transcribe also produces a
        transcription of each item. An item includes the start time, end time,
        and any alternative transcriptions. You can't set both ShowSpeakerLabel
        and EnableChannelIdentification in the same request. If you set both,
        your request returns a BadRequestException.

    :param number_of_channels:
        The number of channels that are in your audio stream.

    :param content_identification_type:
        Indicates whether content identification was enabled for your transcription request.

    :param content_redaction_type:
        Redacts all personally identifiable information (PII) identified in your
        transcript.
        Content redaction is performed at the segment level; PII specified in
        PiiEntityTypes is redacted upon complete transcription of an audio segment.
        You can't set ContentRedactionType and ContentIdentificationType in
        the same request. If you set both, your request returns a BadRequestException.

    :param pii_entity_types:
        Specify which types of personally identifiable information (PII) you
        want to redact in your transcript. You can include as many types as
        you'd like, or you can select ALL.

    :param enable_partial_results_stabilization:
        When true, instructs Amazon Transcribe to present transcription results
        that have the partial results stabilized. Normally, any word or phrase
        from one partial result can change in a subsequent partial result. With
        partial results stabilization enabled, only the last few words of one
        partial result can change in another partial result.

    :param partial_results_stability:
        You can use this field to set the stability level of the transcription
        results. A higher stability level means that the transcription results
        are less likely to change. Higher stability levels can come with lower
        overall transcription accuracy.

    :param language_model_name:
        The name of the language model you want to use.

    :param identify_language:
        Enables automatic language identification for your transcription.

        If you include IdentifyLanguage, you can optionally include a list of
        language codes, using LanguageOptions, that you think may be present
        in your audio stream. Including language options can improve
        transcription accuracy.

        You can also include a preferred language using PreferredLanguage.
        Adding a preferred language can help Amazon Transcribe identify the
        language faster than if you omit this parameter.

        If you have multi-channel audio that contains different languages on
        each channel, and you've enabled channel identification, automatic
        language identification identifies the dominant language on each
        audio channel.

        Note that you must include either LanguageCode or IdentifyLanguage
        in your request. If you include both parameters, your request fails.

        Streaming language identification can't be combined with custom
        language models or redaction.

    :param language_options:
        Specify two or more language codes that represent the languages
        you think may be present in your media; including more than five
        is not recommended. If you're unsure what languages are present,
        do not include this parameter.

        Including language options can improve the accuracy of language
        identification.

        If you include LanguageOptions in your request, you must also
        include IdentifyLanguage.

    :param vocabulary_names:
        Specify the names of the custom vocabularies that you want to use
        when processing your transcription. Note that vocabulary names
        are case sensitive.

        If none of the languages of the specified custom vocabularies
        match the language identified in your media, your job fails.

    :param vocabulary_filter_names:
        Specify the names of the custom vocabulary filters that you want
        to use when processing your transcription. Note that vocabulary
        filter names are case sensitive.

        If none of the languages of the specified custom vocabulary
        filters match the language identified in your media, your job fails.

    """

    def __init__(
        self,
        language_code=None,
        media_sample_rate_hz=None,
        media_encoding=None,
        vocabulary_name=None,
        session_id=None,
        vocab_filter_method=None,
        vocab_filter_name=None,
        show_speaker_label=None,
        enable_channel_identification=None,
        number_of_channels=None,
        content_identification_type=None,
        content_redaction_type=None,
        pii_entity_types=None,
        enable_partial_results_stabilization=None,
        partial_results_stability=None,
        language_model_name=None,
        identify_language=None,
        language_options=None,
        preferred_language=None,
        vocabulary_names=None,
        vocabulary_filter_names=None,
    ):

        self.language_code: Optional[str] = language_code
        self.media_sample_rate_hz: Optional[int] = media_sample_rate_hz
        self.media_encoding: Optional[str] = media_encoding
        self.vocabulary_name: Optional[str] = vocabulary_name
        self.session_id: Optional[str] = session_id
        self.vocab_filter_method: Optional[str] = vocab_filter_method
        self.vocab_filter_name: Optional[str] = vocab_filter_name
        self.show_speaker_label: Optional[bool] = show_speaker_label
        self.enable_channel_identification: Optional[
            bool
        ] = enable_channel_identification
        self.content_identification_type: Optional[str] = content_identification_type
        self.content_redaction_type: Optional[str] = content_redaction_type
        self.pii_entity_types: Optional[str] = pii_entity_types
        self.number_of_channels: Optional[int] = number_of_channels
        self.enable_partial_results_stabilization: Optional[
            bool
        ] = enable_partial_results_stabilization
        self.partial_results_stability: Optional[str] = partial_results_stability
        self.language_model_name: Optional[str] = language_model_name
        self.identify_language: Optional[bool] = identify_language
        self.preferred_language: Optional[str] = preferred_language
        self.language_options: Optional[str] = language_options
        self.vocabulary_names: Optional[str] = vocabulary_names
        self.vocabulary_filter_names: Optional[str] = vocabulary_filter_names


class StartCallAnalyticsStreamTranscriptionRequest:
    """Transcription Request

    :param language_code:
        Indicates the source language used in the input audio stream.

    :param media_sample_rate_hz:
        The sample rate, in Hertz, of the input audio. We suggest that you
        use 8000 Hz for low quality audio and 16000 Hz for high quality audio.

    :param media_encoding:
        The encoding used for the input audio.

    :param vocabulary_name:
        The name of the vocabulary to use when processing the transcription job.

    :param session_id:
        A identifier for the transcription session. Use this parameter when you
        want to retry a session. If you don't provide a session ID,
        Amazon Transcribe will generate one for you and return it in the response.

    :param vocab_filter_method:
        The manner in which you use your vocabulary filter to filter words in
        your transcript.

    :param vocab_filter_name:
        The name of the vocabulary filter you've created that is unique to
        your AWS account. Provide the name in this field to successfully
        use it in a stream.

    :param show_speaker_label:
        When true, enables speaker identification in your real-time stream.

    :param enable_channel_identification:
        When true, instructs Amazon Transcribe to process each audio channel
        separately and then merge the transcription output of each channel
        into a single transcription. Amazon Transcribe also produces a
        transcription of each item. An item includes the start time, end time,
        and any alternative transcriptions. You can't set both ShowSpeakerLabel
        and EnableChannelIdentification in the same request. If you set both,
        your request returns a BadRequestException.

    :param number_of_channels:
        The number of channels that are in your audio stream.

    :param enable_partial_results_stabilization:
        When true, instructs Amazon Transcribe to present transcription results
        that have the partial results stabilized. Normally, any word or phrase
        from one partial result can change in a subsequent partial result. With
        partial results stabilization enabled, only the last few words of one
        partial result can change in another partial result.

    :param partial_results_stability:
        You can use this field to set the stability level of the transcription
        results. A higher stability level means that the transcription results
        are less likely to change. Higher stability levels can come with lower
        overall transcription accuracy.
    :param language_model_name:
        The name of the language model you want to use.
    """

    def __init__(
        self,
        language_code=None,
        media_sample_rate_hz=None,
        media_encoding=None,
        vocabulary_name=None,
        session_id=None,
        vocab_filter_name=None,
        vocab_filter_method=None,
        language_model_name=None,
        enable_partial_results_stabilization=None,
        partial_results_stability=None,
        content_identification_type=None,
        content_redaction_type=None,
        pii_entity_types=None,
    ):
        self.language_code: Optional[str] = language_code
        self.media_sample_rate_hz: Optional[int] = media_sample_rate_hz
        self.media_encoding: Optional[str] = media_encoding
        self.vocabulary_name: Optional[str] = vocabulary_name
        self.session_id: Optional[str] = session_id
        self.vocab_filter_name: Optional[str] = vocab_filter_name
        self.vocab_filter_method: Optional[str] = vocab_filter_method
        self.language_model_name: Optional[str] = language_model_name
        self.enable_partial_results_stabilization: Optional[
            bool
        ] = enable_partial_results_stabilization
        self.partial_results_stability: Optional[str] = partial_results_stability
        self.content_identification_type: Optional[str] = content_identification_type
        self.content_redaction_type: Optional[str] = content_redaction_type
        self.pii_entity_types: Optional[str] = pii_entity_types


class StartStreamTranscriptionResponse:
    """Transcription Response

    :param transcript_result_stream:
        Represents the stream of transcription events from
        Amazon Transcribe to your application.

    :param request_id: An identifier for the streaming transcription.

    :param language_code:
        Indicates the source language used in the input audio stream.

    :param media_sample_rate_hz:
        The sample rate, in Hertz, of the input audio. We suggest that you
        use 8000 Hz for low quality audio and 16000 Hz for high quality audio.

    :param media_encoding:
        The encoding used for the input audio.

    :param session_id:
        A identifier for the transcription session. Use this parameter when you
        want to retry a session. If you don't provide a session ID,
        Amazon Transcribe will generate one for you and return it in the response.

    :param vocab_filter_name:
        The name of the vocabulary filter used in your real-time stream.

    :param vocab_filter_method:
        The manner in which you use your vocabulary filter to filter words in
        your transcript.

    :param show_speaker_label:
        Shows whether speaker identification was enabled in the stream.

    :param enable_channel_identification:
        Shows whether channel identification has been enabled in the stream.

    :param number_of_channels:
        The number of channels identified in the stream.

    :param enable_partial_results_stabilization:
        Shows whether partial results stabilization has been enabled in the
        stream.

    :param partial_results_stability:
        If partial results stabilization has been enabled in the stream,
        shows the stability level.

    :param language_model_name:
        The name of the custom language model used in the transcription.
    """

    def __init__(
        self,
        transcript_result_stream,
        request_id=None,
        language_code=None,
        media_sample_rate_hz=None,
        media_encoding=None,
        vocabulary_name=None,
        session_id=None,
        vocab_filter_name=None,
        vocab_filter_method=None,
        show_speaker_label=None,
        enable_channel_identification=None,
        number_of_channels=None,
        enable_partial_results_stabilization=None,
        partial_results_stability=None,
        language_model_name=None,
    ):
        self.request_id: Optional[str] = request_id
        self.language_code: Optional[str] = language_code
        self.media_sample_rate_hz: Optional[int] = media_sample_rate_hz
        self.media_encoding: Optional[str] = media_encoding
        self.vocabulary_name: Optional[str] = vocabulary_name
        self.session_id: Optional[str] = session_id
        self.transcript_result_stream: TranscriptResultStream = transcript_result_stream
        self.vocab_filter_name: Optional[str] = vocab_filter_name
        self.vocab_filter_method: Optional[str] = vocab_filter_method
        self.show_speaker_label: Optional[bool] = show_speaker_label
        self.enable_channel_identification: Optional[
            bool
        ] = enable_channel_identification
        self.number_of_channels: Optional[int] = number_of_channels
        self.enable_partial_results_stabilization: Optional[
            bool
        ] = enable_partial_results_stabilization
        self.partial_results_stability: Optional[str] = partial_results_stability
        self.language_model_name: Optional[str] = language_model_name


class StartCallAnalyticsStreamTranscriptionResponse:
    """Transcription Response

    :param transcript_result_stream:
        Represents the stream of transcription events from
        Amazon Transcribe to your application.

    :param request_id: An identifier for the streaming transcription.

    :param language_code:
        Indicates the source language used in the input audio stream.

    :param media_sample_rate_hz:
        The sample rate, in Hertz, of the input audio. We suggest that you
        use 8000 Hz for low quality audio and 16000 Hz for high quality audio.

    :param media_encoding:
        The encoding used for the input audio.

    :param session_id:
        A identifier for the transcription session. Use this parameter when you
        want to retry a session. If you don't provide a session ID,
        Amazon Transcribe will generate one for you and return it in the response.

    :param vocab_filter_name:
        The name of the vocabulary filter used in your real-time stream.

    :param vocab_filter_method:
        The manner in which you use your vocabulary filter to filter words in
        your transcript.

    :param show_speaker_label:
        Shows whether speaker identification was enabled in the stream.

    :param enable_channel_identification:
        Shows whether channel identification has been enabled in the stream.

    :param number_of_channels:
        The number of channels identified in the stream.

    :param enable_partial_results_stabilization:
        Shows whether partial results stabilization has been enabled in the
        stream.

    :param partial_results_stability:
        If partial results stabilization has been enabled in the stream,
        shows the stability level.

    :param language_model_name:
        The name of the custom language model used in the transcription.
    """

    def __init__(
        self,
        transcript_result_stream,
        request_id=None,
        language_code=None,
        media_sample_rate_hz=None,
        media_encoding=None,
        vocabulary_name=None,
        session_id=None,
        vocab_filter_name=None,
        vocab_filter_method=None,
        language_model_name=None,
        enable_partial_results_stabilization=None,
        partial_results_stability=None,
        content_identification_type=None,
        content_redaction_type=None,
        pii_entity_types=None,
    ):
        self.request_id: Optional[str] = request_id
        self.language_code: Optional[str] = language_code
        self.media_sample_rate_hz: Optional[int] = media_sample_rate_hz
        self.media_encoding: Optional[str] = media_encoding
        self.vocabulary_name: Optional[str] = vocabulary_name
        self.session_id: Optional[str] = session_id
        self.transcript_result_stream: TranscriptResultStream = transcript_result_stream
        self.vocab_filter_name: Optional[str] = vocab_filter_name
        self.vocab_filter_method: Optional[str] = vocab_filter_method
        self.enable_partial_results_stabilization: Optional[
            bool
        ] = enable_partial_results_stabilization
        self.partial_results_stability: Optional[str] = partial_results_stability
        self.language_model_name: Optional[str] = language_model_name
        self.content_identification_type: Optional[str] = content_identification_type
        self.content_redaction_type: Optional[str] = content_redaction_type
        self.pii_entity_types: Optional[str] = pii_entity_types


class Transcript:
    """The transcription in a TranscriptEvent.

    :param results:
        Result objects that contain the results of transcribing a portion of the
        input audio stream. The array can be empty.
    """

    def __init__(self, results: List[Result]):
        self.results = results


class TranscriptEvent(BaseEvent):
    """Represents a set of transcription results from the server to the client.
    It contains one or more segments of the transcription.

    :param transcript:
        The transcription of the audio stream. The transcription is composed of
        all of the items in the results list.
    """

    def __init__(self, transcript: Transcript):
        self.transcript = transcript


class TranscriptResultStream(EventStream):
    """Transcription result stream containing returned TranscriptEvent output.

    Results are surfaced through the async iterator interface (i.e. async for)

    :raises BadRequestException:
        A client error occurred when the stream was created. Check the parameters
        of the request and try your request again.

    :raises LimitExceededException:
        Your client has exceeded one of the Amazon Transcribe limits, typically
        the limit on audio length. Break your audio stream into smaller chunks
        and try your request again.

    :raises InternalFailureException:
        A problem occurred while processing the audio.
        Amazon Transcribe terminated processing.

    :raises ConflictException:
        A new stream started with the same session ID.
        The current stream has been terminated.

    :raises ServiceUnavailableException:
        Service is currently unavailable. Try your request later.
    """


class ChannelDefinition:
    """Channel Definition for Transcribe Call Analytics

    Indicates which speaker is on which channel

    :param channel_id:
        Specify the audio channel you want to define.

    :param participant_role:
        Specify the speaker you want to define. Omitting this parameter
        is equivalent to specifying both participants.
        Valid values are AGENT or CUSTOMER only.

    """

    def __init__(self, channel_id, participant_role):
        self.channel_id: int = channel_id
        self.participant_role: str = participant_role

    @property
    def __json__(self):
        return {"ChannelId": self.channel_id, "ParticipantRole": self.participant_role}


class PostCallAnalyticsSettings:
    """Post Call Analytics Settings for Transcribe Call Analytics

    :param output_location:
        The Amazon S3 location where you want your Call Analytics transcription output stored.

    :param data_access_role_arn:
        The Amazon Resource Name (ARN) of an IAM role that has permissions to access the
        Amazon S3 bucket that contains your input files. If the role that you specify
        doesn't have the appropriate permissions to access the specified Amazon S3
        location, your request fails.

    :param output_encryption_kms_key_id:
        The KMS key you want to use to encrypt your Call Analytics output.
        Optional

    :param content_redaction_output:
        Specify whether you want only a redacted transcript or both a redacted and an
        unredacted transcript. If you choose redacted and unredacted, two JSON files
        are generated and stored in the Amazon S3 output location you specify.

        Note that to include ContentRedactionOutput in your request, you must enable
        content redaction (ContentRedactionType).

    """

    def __init__(
        self,
        output_location,
        data_access_role_arn,
        output_encryption_kms_key_id=None,
        content_redaction_output=None,
    ):
        self.output_location = output_location
        self.data_access_role_arn = data_access_role_arn
        self.output_encryption_kms_key_id = output_encryption_kms_key_id
        self.content_redaction_output = content_redaction_output

    @property
    def __json__(self):
        response = {
            "OutputLocation": self.output_location,
            "DataAccessRoleArn": self.data_access_role_arn,
        }

        if self.output_encryption_kms_key_id is not None:
            response["OutputEncryptionKMSKeyId"] = self.output_encryption_kms_key_id

        if self.content_redaction_output is not None:
            response["ContentRedactionOutput"] = self.content_redaction_output

        return response


class ConfigurationEvent(BaseEvent):
    """Provides a wrapper for the configuration event

    :param channel_definitions:
        Channel definitions

    :param post_call_analytics_settings:
        Post Call Analytics Settings

    """

    def __init__(self, channel_definitions, post_call_analytics_settings=None):
        self.channel_definitions: List[ChannelDefinition] = channel_definitions
        self.post_call_analytics_settings: Optional[
            PostCallAnalyticsSettings
        ] = post_call_analytics_settings

    @property
    def __json__(self):
        response = {"ChannelDefinitions": [c.__json__ for c in self.channel_definitions]}

        if self.post_call_analytics_settings is not None:
            response["PostCallAnalyticsSettings"] = self.post_call_analytics_settings.__json__

        return response


class UtteranceEvent(BaseEvent):
    """Utterance Event Details Here
        Contains set of transcription results from one or more audio segments, along with
        additional information about the parameters included in your request. For example,
        channel definitions, partial result stabilization, sentiment, and issue detection.

    :param utterance_id:
        The unique identifier that is associated with the specified UtteranceEvent.

    :param is_partial:
        Indicates whether the segment in the UtteranceEvent is complete (FALSE) or partial (TRUE).

    :param participant_role:
        Provides the role of the speaker for each audio channel, either CUSTOMER or AGENT.

    :param begin_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the start of the identified item.

    :param end_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the end of the identified item.

    :param transcript:
        Contains transcribed text.

    :param items:
        Contains words, phrases, or punctuation marks that are associated with the specified UtteranceEvent

    :param entities:
        Contains entities identified as personally identifiable information (PII) in your transcription output.

    :param sentiment:
        Provides the sentiment that was detected in the specified segment.

    :param issues_detected:
        Provides the issue that was detected in the specified segment.
    """

    def __init__(
        self,
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
    ):
        self.utterance_id: str = utterance_id
        self.is_partial: bool = is_partial
        self.participant_role: str = participant_role
        self.begin_offset_millis: float = begin_offset_millis
        self.end_offset_millis: float = end_offset_millis
        self.transcript: str = transcript
        self.items: List[CallAnalyticsItem] = items
        self.entities: List[CallAnalyticsEntity] = entities
        self.sentiment: str = sentiment
        self.issues_detected: List[IssueDetected] = issues_detected


class IssueDetected:
    """Issue Detected
        Lists the issues that were identified in your audio segment.

    :param character_offsets:
        Provides the timestamps that identify when in an audio segment the specified issue occurs.

    """

    def __init__(self, character_offsets):
        self.character_offsets: CharacterOffsets = character_offsets


class CharacterOffsets:
    """Character Offsets
        Provides the location, using character count, in your transcript where a match is
        identified. For example, the location of an issue or a category match within a segment.

    :param begin:
        Provides the character count of the first character where a match is identified. For
        example, the first character associated with an issue or a category match in a segment transcript.

    :param end:
        Provides the character count of the last character where a match is identified. For example,
        the last character associated with an issue or a category match in a segment transcript.

    """

    def __init__(self, begin, end):
        self.begin: float = begin
        self.end: float = end


class CallAnalyticsItem:
    """Call Analytics Item
        A word, phrase, or punctuation mark in your Call Analytics transcription
        output, along with various associated attributes, such as confidence score,
        type, and start and end times.

    :param begin_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the start of the identified item.

    :param end_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the end of the identified item.

    :param item_type:
        The type of item identified. Options are: PRONUNCIATION (spoken words) and PUNCTUATION.

    :param content:
        The word or punctuation that was transcribed.

    :param confidence:
        The confidence score associated with a word or phrase in your transcript.
        Confidence scores are values between 0 and 1. A larger value indicates a higher probability
        that the identified item correctly matches the item spoken in your media

    :param vocabulary_filter_match:
        Indicates whether the specified item matches a word in the vocabulary filter included in your
        Call Analytics request. If true, there is a vocabulary filter match.

    :param stable:
        If partial result stabilization is enabled, Stable indicates whether the specified
        item is stable (true) or if it may change when the segment is complete (false).

    """

    def __init__(
        self,
        begin_offset_millis,
        end_offset_millis,
        item_type,
        content,
        confidence,
        vocabulary_filter_match,
        stable,
    ):
        self.begin_offset_millis = begin_offset_millis
        self.end_offset_millis = end_offset_millis
        self.item_type = item_type
        self.content = content
        self.confidence = confidence
        self.vocabulary_filter_match = vocabulary_filter_match
        self.stable = stable


class Entity:
    """Entity
        Contains entities identified as personally identifiable information (PII) in your
        transcription output, along with various associated attributes. Examples include
        category, confidence score, type, stability score, and start and end times.

    :param category:
        The category of information identified. The only category is PII.

    :param confidence:
        The confidence score associated with the identified PII entity in your audio.

        Confidence scores are values between 0 and 1. A larger value indicates a higher
        probability that the identified entity correctly matches the entity spoken in your media.

    :param content:
        The word or words identified as PII.

    :param end_time:
        The end time, in milliseconds, of the utterance that was identified as PII.

    :param start_time:
        The start time, in milliseconds, of the utterance that was identified as PII.

    :param type:
        The type of PII identified. For example, NAME or CREDIT_DEBIT_NUMBER.

    """

    def __init__(
        self,
        category,
        confidence,
        content,
        end_time,
        start_time,
        type,
    ):
        self.category = category
        self.confidence = confidence
        self.content = content
        self.end_time = end_time
        self.start_time = start_time
        self.type = type


class CallAnalyticsEntity:
    """Call Analytics Entity
        Contains entities identified as personally identifiable information (PII) in
        your transcription output, along with various associated attributes. Examples
        include category, confidence score, content, type, and start and end times.

    :param begin_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the start of the identified entity.

    :param end_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the end of the identified entity.

    :param category:
        The category of information identified. For example, PII.

    :param entity_type:
        The type of PII identified. For example, NAME or CREDIT_DEBIT_NUMBER.

    :param content:
        The word or words that represent the identified entity.

    :param confidence:
        The confidence score associated with the identification of an entity in your transcript.
        Confidence scores are values between 0 and 1. A larger value indicates a higher probability that the
        identified entity correctly matches the entity spoken in your media.

    """

    def __init__(
        self,
        begin_offset_millis,
        end_offset_millis,
        category,
        entity_type,
        content,
        confidence,
    ):
        self.begin_offset_millis = begin_offset_millis
        self.end_offset_millis = end_offset_millis
        self.category = category
        self.entity_type = entity_type
        self.content = content
        self.confidence = confidence


class CategoryEvent(BaseEvent):
    """Category Event Details

        Provides information on any TranscriptFilterType categories that matched
        your transcription output. Matches are identified for each segment upon
        completion of that segment.

    :param matched_categories:
        Lists the categories that were matched in your audio segment.

    :param matched_details:
        Contains information about the matched categories, including category names and timestamps.

    """

    def __init__(self, matched_categories, matched_details):
        self.matched_categories: List[str] = matched_categories
        self.matched_details: Dict[str, PointsOfInterest] = matched_details


class PointsOfInterest:
    """Points of Interest Details
        Contains the timestamps of matched categories.

    :param timestamp_ranges:
        Contains the timestamp ranges (start time through end time) of matched categories and rules.

    """

    def __init__(self, timestamp_ranges):
        self.timestamp_ranges: List[TimestampRange] = timestamp_ranges


class TimestampRange:
    """Timestamp Details
        Contains the timestamp range (start time through end time) of a matched category.

    :param begin_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the start of the category match.

    :param end_offset_millis:
        The time, in milliseconds, from the beginning of the audio stream to the end of the category match.

    """

    def __init__(self, begin_offset_millis: float, end_offset_millis: float):
        self.begin_offset_millis = begin_offset_millis
        self.end_offset_millis = end_offset_millis


class CallAnalyticsTranscriptResultStream(EventStream):
    """Transcription result stream containing returned UtteranceEvent or CategoryEvent output.

    Results are surfaced through the async iterator interface (i.e. async for)

    :raises BadRequestException:
        A client error occurred when the stream was created. Check the parameters
        of the request and try your request again.

    :raises LimitExceededException:
        Your client has exceeded one of the Amazon Transcribe limits, typically
        the limit on audio length. Break your audio stream into smaller chunks
        and try your request again.

    :raises InternalFailureException:
        A problem occurred while processing the audio.
        Amazon Transcribe terminated processing.

    :raises ConflictException:
        A new stream started with the same session ID.
        The current stream has been terminated.

    :raises ServiceUnavailableException:
        Service is currently unavailable. Try your request later.
    """


class StartStreamTranscriptionEventStream:
    """Event stream wrapper containing both input and output interfaces to
    Amazon Transcribe. This should only be created by the client.

    :param audio_stream:
        Audio input stream generated by client for new transcription requests.

    :param response: Response object from Amazon Transcribe.
    """

    def __init__(self, audio_stream: AudioStream, response):
        self._response = response
        self._audio_stream = audio_stream

    @property
    def response(self) -> StartStreamTranscriptionResponse:
        """Response object from Amazon Transcribe containing metadata and
        response output stream.
        """
        return self._response

    @property
    def input_stream(self) -> AudioStream:
        """Audio stream to Amazon Transcribe that takes input audio."""
        return self._audio_stream

    @property
    def output_stream(self) -> TranscriptResultStream:
        """Response stream containing transcribed event output."""
        return self.response.transcript_result_stream


class StartCallAnalyticsStreamTranscriptionEventStream:
    """Event stream wrapper containing both input and output interfaces to
    Amazon Transcribe. This should only be created by the client.

    :param audio_stream:
        Audio input stream generated by client for new transcription requests.

    :param response: Response object from Amazon Transcribe.
    """

    def __init__(self, audio_stream: AudioStream, response):
        self._response = response
        self._audio_stream = audio_stream

    @property
    def response(self) -> StartCallAnalyticsStreamTranscriptionResponse:
        """Response object from Amazon Transcribe containing metadata and
        response output stream.
        """
        return self._response

    @property
    def input_stream(self) -> AudioStream:
        """Audio stream to Amazon Transcribe that takes input audio."""
        return self._audio_stream

    @property
    def output_stream(self) -> TranscriptResultStream:
        """Response stream containing transcribed event output."""
        return self.response.transcript_result_stream
