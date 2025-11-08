package dev.wenslo.trueshotodds.service;

import dev.wenslo.trueshotodds.dto.polls.CreatePollRequest;
import dev.wenslo.trueshotodds.dto.response.LeaderboardEntryResponse;
import dev.wenslo.trueshotodds.entity.Poll;
import dev.wenslo.trueshotodds.repository.PollRepository;
import dev.wenslo.trueshotodds.repository.VoteRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.Optional;

@Service
@Slf4j
public class PollService {

    private final VoteRepository voteRepository;
    private final PollRepository pollRepository;

    public PollService(VoteRepository voteRepository, PollRepository pollRepository) {
        this.voteRepository = voteRepository;
        this.pollRepository = pollRepository;
    }

    /**
     * Get the top 10 predictors who voted with the majority on closed polls
     * @return List of top 10 users with their correct prediction counts
     */
    @Transactional(readOnly = true)
    public List<LeaderboardEntryResponse> getTopPredictors() {
        return voteRepository.findTopPredictors(PageRequest.of(0, 10));
    }

    /**
     * Create a new poll and deactivate the current active poll
     * @param request The poll creation request
     * @return The created poll as a response DTO
     */
    @Transactional
    public Poll createPoll(CreatePollRequest request) {
        log.info("Creating new poll with question: {}", request.getQuestion());

        // 1. Deactivate current active poll (if exists)
        Optional<Poll> currentActivePoll = pollRepository.findFirstByIsActiveTrue();
        if (currentActivePoll.isPresent()) {
            Poll activePoll = currentActivePoll.get();
            activePoll.setIsActive(false);
            activePoll.setClosedAt(LocalDateTime.now());
            pollRepository.save(activePoll);
            log.info("Deactivated previous poll with ID: {}", activePoll.getId());
        }

        // 2. Parse the endsAt timestamp
        LocalDateTime endsAt;
        try {
            endsAt = LocalDateTime.parse(request.getEndsAt());
        } catch (DateTimeParseException e) {
            log.error("Failed to parse endsAt timestamp: {}", request.getEndsAt());
            throw new IllegalArgumentException("Invalid endsAt format. Expected ISO-8601 format (e.g., 2024-12-31T23:59:59)");
        }

        // 3. Create new Poll entity
        Poll newPoll = new Poll();
        newPoll.setQuestion(request.getQuestion());
        newPoll.setDescription(request.getDescription());
        newPoll.setOptionAText(request.getOptionAText());
        newPoll.setOptionBText(request.getOptionBText());
        newPoll.setEndsAt(endsAt);
        newPoll.setIsActive(true);
        newPoll.setOptionAVotes(0);
        newPoll.setOptionBVotes(0);
        newPoll.setMarketTicker(request.getKalshiMarketTicker());
        newPoll.setSeriesTicker(request.getKalshiSeriesTicker());

        // 4. Save to database
        Poll savedPoll = pollRepository.save(newPoll);
        log.info("Created new poll with ID: {}", savedPoll.getId());

        return newPoll;
    }

    /**
     * Get all expired polls (active polls where endsAt is in the past)
     * @return List of expired polls
     */
    @Transactional(readOnly = true)
    public List<Poll> getExpiredPolls() {
        return pollRepository.findExpiredPolls(LocalDateTime.now());
    }

    /**
     * Mark a poll as inactive
     * @param pollId The ID of the poll to mark inactive
     */
    @Transactional
    public void markPollInactive(Long pollId) {
        log.info("Marking poll {} as inactive", pollId);
        Poll poll = pollRepository.findById(pollId)
                .orElseThrow(() -> new IllegalArgumentException("Poll not found with ID: " + pollId));

        poll.setIsActive(false);
        poll.setClosedAt(LocalDateTime.now());
        pollRepository.save(poll);
        log.info("Poll {} marked as inactive", pollId);
    }
}
