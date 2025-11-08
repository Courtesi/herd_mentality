package dev.wenslo.trueshotodds.dto.polls;

import dev.wenslo.trueshotodds.entity.Poll;
import lombok.Data;

@Data
public class CreatePollResponse {
    private boolean success;
    private String message;

    private Poll poll;

    public CreatePollResponse(boolean success, String message, Poll poll) {
        this.success = success;
        this.message = message;
        this.poll = poll;
    }

    public static CreatePollResponse success(Poll poll) {
        return new CreatePollResponse(true, "Poll created successfully", poll);
    }

    public static CreatePollResponse error(String errorMessage) {
        return new CreatePollResponse(false, errorMessage, null);
    }
}
