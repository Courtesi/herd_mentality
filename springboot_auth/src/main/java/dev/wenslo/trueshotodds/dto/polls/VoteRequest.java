package dev.wenslo.trueshotodds.dto.polls;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public class VoteRequest {

    @NotNull(message = "Poll ID is required")
    private Long pollId;

    @NotNull(message = "Option voted is required")
    @Pattern(regexp = "^[AB]$", message = "Option voted must be 'A' or 'B'")
    private String optionVoted;

    // Constructors
    public VoteRequest() {}

    public VoteRequest(Long pollId, String optionVoted) {
        this.pollId = pollId;
        this.optionVoted = optionVoted;
    }

    // Getters and Setters
    public Long getPollId() {
        return pollId;
    }

    public void setPollId(Long pollId) {
        this.pollId = pollId;
    }

    public String getOptionVoted() {
        return optionVoted;
    }

    public void setOptionVoted(String optionVoted) {
        this.optionVoted = optionVoted;
    }
}
