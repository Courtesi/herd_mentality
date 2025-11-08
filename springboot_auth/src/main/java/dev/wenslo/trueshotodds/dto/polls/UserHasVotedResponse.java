package dev.wenslo.trueshotodds.dto.polls;

import lombok.Data;

@Data
public class UserHasVotedResponse {

    private boolean success;
    private String message;

    private boolean hasVoted;
    private String optionVoted;
    private String votedAt;

    public UserHasVotedResponse(boolean success, String message, boolean hasVoted, String optionVoted, String votedAt) {
        this.success = success;
        this.message = message;
        this.hasVoted = hasVoted;
        this.optionVoted = optionVoted;
        this.votedAt = votedAt;
    }

    public static UserHasVotedResponse error(String errorMessage) {
        return new UserHasVotedResponse(false, errorMessage, false, null, null);
    }

    public static UserHasVotedResponse success(boolean hasVoted, String optionVoted, String votedAt) {
        return new UserHasVotedResponse(true, "Response grabbed successfully", hasVoted, optionVoted, votedAt);
    }
}
