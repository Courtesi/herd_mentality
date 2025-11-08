package dev.wenslo.trueshotodds.dto.polls;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CreatePollRequest {

    @NotBlank(message = "Question is required")
    private String question;

    private String description;

    @NotBlank(message = "Option A text is required")
    private String optionAText;

    @NotBlank(message = "Option B text is required")
    private String optionBText;

    @NotNull(message = "End date/time is required")
    private String endsAt;

    private String kalshiSeriesTicker;

    private String kalshiMarketTicker;

    private String pollType;
}
