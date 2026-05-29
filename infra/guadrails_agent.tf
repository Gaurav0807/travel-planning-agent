
resource "aws_bedrock_guardrail" "travel_agent_guardrail" {
    name = "travel-agents-guadrail"
    description = "Guadrails for Agents call"

    blocked_input_messaging = "I can't process that request. How can I help with travel planning ?"
    blocked_outputs_messaging = "I can't process that request. Let me help with your travel plans instead"
    # Content Filters
    content_policy_config {
      filters_config {
        type            = "HATE"
        input_strength  = "HIGH"
        output_strength = "HIGH"
      }
      filters_config {
        type            = "VIOLENCE"
        input_strength  = "HIGH"
        output_strength = "HIGH"
      }
      filters_config {
        type            = "SEXUAL"
        input_strength  = "HIGH"
        output_strength = "HIGH"
      }
      filters_config {
        type            = "INSULTS"
        input_strength  = "MEDIUM"
        output_strength = "MEDIUM"
      }
      filters_config {
        type            = "MISCONDUCT"
        input_strength  = "HIGH"
        output_strength = "HIGH"
      }
      filters_config {
        type            = "PROMPT_ATTACK"
        input_strength  = "HIGH"
        output_strength = "NONE"
      }
    }

    # PII Filters
    sensitive_information_policy_config {
      pii_entities_config {
        type   = "US_SOCIAL_SECURITY_NUMBER"
        action = "BLOCK"
      }
      pii_entities_config {
        type   = "CREDIT_DEBIT_CARD_NUMBER"
        action = "BLOCK"
      }
      pii_entities_config {
        type   = "EMAIL"
        action = "ANONYMIZE"
      }
      pii_entities_config {
        type   = "PHONE"
        action = "ANONYMIZE"
      }
    }

    # Topic Filters
    topic_policy_config {
      topics_config {
        name       = "Competitors"
        definition = "Discussion about competitor travel platforms"
        examples   = ["Should I use Expedia?", "Booking.com prices"]
        type       = "DENY"
      }
      topics_config {
        name       = "OffTopic"
        definition = "Requests unrelated to travel planning like coding, homework, technical help"
        examples   = [
          "Write Python code for me",
          "Help with my homework"
        ]
        type       = "DENY"
      }
    }

    # Word Filters
    word_policy_config {
      words_config {
        text = "jailbreak"
      }
      words_config {
        text = "damn"
      }
      words_config {
        text = "dammit"
      }
      managed_word_lists_config {
        type = "PROFANITY"
      }
    }

}

resource "aws_ssm_parameter" "guardrail_id" {
    name = "/travel-agent/guardrail-id"
    type = "String"
    value = aws_bedrock_guardrail.travel_agent_guardrail.guardrail_id
    tags = {
        Project = "Agent-Guardrail"
    }
  
}

output "guardrail_id" {
    value = aws_bedrock_guardrail.travel_agent_guardrail.guardrail_id
}