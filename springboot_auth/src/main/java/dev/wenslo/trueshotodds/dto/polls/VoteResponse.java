package dev.wenslo.trueshotodds.dto.polls;

import dev.wenslo.trueshotodds.entity.Poll;
import lombok.Data;

@Data
public class VoteResponse {

    private boolean success;
    private String message;
    private String optionVoted;
    private Poll poll;

    public VoteResponse(boolean success, String message, String optionVoted, Poll poll) {
        this.success = success;
        this.message = message;
        this.optionVoted = optionVoted;
        this.poll = poll;
    }

    public static VoteResponse success(String optionVoted, Poll poll) {
        return new VoteResponse(true, "Vote submitted successfully", optionVoted, poll);
    }

    public static VoteResponse error(String errorMessage) {
        return new VoteResponse(false, errorMessage, "", null);
    }
}
