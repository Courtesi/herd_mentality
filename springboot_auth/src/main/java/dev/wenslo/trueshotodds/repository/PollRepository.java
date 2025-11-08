package dev.wenslo.trueshotodds.repository;

import dev.wenslo.trueshotodds.entity.Poll;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface PollRepository extends JpaRepository<Poll, Long> {

    /**
     * Find the most recent poll
     */
    Optional<Poll> findFirstByOrderByCreatedAtDesc();

    /**
     * Find the currently active poll
     */
    Optional<Poll> findFirstByIsActiveTrue();

    /**
     * Find all active polls that have expired (endsAt is in the past)
     */
    @Query("SELECT p FROM Poll p WHERE p.isActive = true AND p.endsAt < :now")
    List<Poll> findExpiredPolls(@Param("now") LocalDateTime now);

    /**
     * Find polls closed within a date range
     */
    List<Poll> findByClosedAtBetween(LocalDateTime start, LocalDateTime end);

    /**
     * Find all polls that have been explicitly closed
     */
    List<Poll> findByClosedAtIsNotNull();

    /**
     * Find all polls that have never been explicitly closed
     */
    List<Poll> findByClosedAtIsNull();
}