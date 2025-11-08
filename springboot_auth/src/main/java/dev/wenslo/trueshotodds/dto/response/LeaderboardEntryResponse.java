package dev.wenslo.trueshotodds.dto.response;

public class LeaderboardEntryResponse {
    private String userId;
    private String fullName;
    private String profilePictureUrl;
    private Long correctPredictionsCount;

    public LeaderboardEntryResponse(String userId, String fullName, String profilePictureUrl, Long correctPredictionsCount) {
        this.userId = userId;
        this.fullName = fullName;
        this.profilePictureUrl = profilePictureUrl;
        this.correctPredictionsCount = correctPredictionsCount;
    }

    public String getUserId() {
        return userId;
    }

    public String getFullName() {
        return fullName;
    }

    public String getProfilePictureUrl() {
        return profilePictureUrl;
    }

    public Long getCorrectPredictionsCount() {
        return correctPredictionsCount;
    }
}
