package dev.wenslo.trueshotodds.repository;

import dev.wenslo.trueshotodds.dto.response.LeaderboardEntryResponse;
import dev.wenslo.trueshotodds.entity.Poll;
import dev.wenslo.trueshotodds.entity.User;
import dev.wenslo.trueshotodds.entity.Vote;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface VoteRepository extends JpaRepository<Vote, Long> {

    /**
     * Find a vote by poll and user
     */
    Optional<Vote> findByPollAndUser(Poll poll, User user);

    /**
     * Check if a user has voted on a specific poll
     */
    boolean existsByPollAndUser(Poll poll, User user);

    /**
     * Find a vote by poll ID and user ID
     */
    Optional<Vote> findByPoll_IdAndUser_Id(Long pollId, String userId);

    /**
     * Find top predictors who voted with the majority on closed polls
     * Excludes tied polls where optionAVotes equals optionBVotes
     */
    @Query("SELECT v.user.id as userId, v.user.fullName as fullName, " +
           "v.user.profilePictureUrl as profilePictureUrl, " +
           "COUNT(v) as correctPredictionsCount " +
           "FROM Vote v JOIN v.poll p " +
           "WHERE p.isActive = false AND p.optionAVotes != p.optionBVotes AND " +
           "((p.optionAVotes > p.optionBVotes AND v.optionVoted = 'A') OR " +
           " (p.optionBVotes > p.optionAVotes AND v.optionVoted = 'B')) " +
           "GROUP BY v.user.id, v.user.fullName, v.user.profilePictureUrl " +
           "ORDER BY COUNT(v) DESC")
    List<LeaderboardEntryResponse> findTopPredictors(Pageable pageable);
}
