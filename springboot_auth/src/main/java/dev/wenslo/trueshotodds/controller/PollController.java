package dev.wenslo.trueshotodds.controller;

import dev.wenslo.trueshotodds.dto.polls.*;
import dev.wenslo.trueshotodds.dto.response.LeaderboardEntryResponse;
import dev.wenslo.trueshotodds.entity.Poll;
import dev.wenslo.trueshotodds.entity.User;
import dev.wenslo.trueshotodds.entity.Vote;
import dev.wenslo.trueshotodds.repository.PollRepository;
import dev.wenslo.trueshotodds.repository.UserRepository;
import dev.wenslo.trueshotodds.repository.VoteRepository;
import dev.wenslo.trueshotodds.service.PollService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/polls")
@Slf4j
@Tag(name = "Poll", description = "Voting, poll info management endpoints")
public class PollController {

    @Autowired
    private PollRepository pollRepository;

    @Autowired
    private VoteRepository voteRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PollService pollService;

    @Value("${INTERNAL_API_KEY}")
    private String internalApiKey;

    @GetMapping
    @Operation(summary = "Get latest poll", description = "Returns the latest poll whether or not active")
    public ResponseEntity<Poll> getLatestPoll() {
        Optional<Poll> poll = pollRepository.findFirstByOrderByCreatedAtDesc();

        if (poll.isPresent()) {
            return ResponseEntity.ok(poll.get());
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping("/create")
    @Operation(summary = "Create a poll", description = "Used to create a poll")
    public ResponseEntity<CreatePollResponse> createPoll(
            @Valid @RequestBody CreatePollRequest request,
            @RequestHeader(value = "X-Internal-API-Key", required = false) String apiKey) {

        if (internalApiKey == null || !internalApiKey.equals(apiKey)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(CreatePollResponse.error("Invalid API key"));
        }

        try {
            Poll createdPoll = pollService.createPoll(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(CreatePollResponse.success(createdPoll));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    CreatePollResponse.error("Failed to create poll: " + e.getMessage())
            );
        }
    }

    @PostMapping("/vote")
    @Operation(summary = "Vote for active poll", description = "Lets users vote for the active poll")
    public ResponseEntity<VoteResponse> submitVote(@Valid @RequestBody VoteRequest voteRequest, Authentication authentication) {
        // Check if user is authenticated
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(VoteResponse.error("Unauthorized"));
        }

        // Get current user email from authentication
        String userEmail = authentication.getName();

        // Find the user
        Optional<User> userOpt = userRepository.findByEmailIgnoreCase(userEmail);
        if (userOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(VoteResponse.error("User not found"));
        }

        User user = userOpt.get();

        // Find the poll
        Optional<Poll> pollOpt = pollRepository.findById(voteRequest.getPollId());
        if (pollOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(VoteResponse.error("Poll not found"));
        }

        Poll poll = pollOpt.get();

        // Check if poll is active
        if (!poll.getIsActive()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(VoteResponse.error("This poll has ended"));
        }

        // Check if user already voted
        if (voteRepository.existsByPollAndUser(poll, user)) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(VoteResponse.error("You have already voted for this poll"));
        }

        // Create and save the vote
        Vote vote = new Vote(poll, user, voteRequest.getOptionVoted());
        voteRepository.save(vote);

        // Update vote count in poll
        if ("A".equals(voteRequest.getOptionVoted())) {
            poll.setOptionAVotes(poll.getOptionAVotes() + 1);
        } else {
            poll.setOptionBVotes(poll.getOptionBVotes() + 1);
        }
        pollRepository.save(poll);

        return ResponseEntity.ok(VoteResponse.success(voteRequest.getOptionVoted(), poll));
    }

    @GetMapping("/{pollId}/user-vote")
    @Operation(summary = "Gets user's vote status on poll", description = "Returns whether or not a user has voted on a specific poll")
    public ResponseEntity<UserHasVotedResponse> getUserVote(@PathVariable Long pollId, Authentication authentication) {
        // Check if user is authenticated
        if (authentication == null || !authentication.isAuthenticated()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(UserHasVotedResponse.error("User not authenticated"));
        }

        // Get current user email from authentication
        String userEmail = authentication.getName();

        // Find the user
        Optional<User> userOpt = userRepository.findByEmailIgnoreCase(userEmail);
        if (userOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(UserHasVotedResponse.error("User not found"));
        }

        User user = userOpt.get();

        // Find the vote
        Optional<Vote> voteOpt = voteRepository.findByPoll_IdAndUser_Id(pollId, user.getId());

        if (voteOpt.isPresent()) {
            Vote vote = voteOpt.get();
            return ResponseEntity.ok(UserHasVotedResponse.success(true, vote.getOptionVoted(), vote.getVotedAt().toString()));
        } else {
            return ResponseEntity.ok(UserHasVotedResponse.success(false, "", ""));
        }
    }

    @GetMapping("/leaderboard")
    @Operation(summary = "Get leaderboard", description = "Returns top 10 of users who've voted (ranked by most number of polls aligning with the majority vote)")
    public ResponseEntity<List<LeaderboardEntryResponse>> getLeaderboard() {
        List<LeaderboardEntryResponse> topPredictors = pollService.getTopPredictors();
        return ResponseEntity.ok(topPredictors);
    }

    @GetMapping("/expired")
    @Operation(summary = "Get expired polls", description = "Returns all active polls that have passed their end time")
    public ResponseEntity<List<Poll>> getExpiredPolls() {
        List<Poll> expiredPolls = pollService.getExpiredPolls();
        return ResponseEntity.ok(expiredPolls);
    }

    @GetMapping("/closed")
    @Operation(summary = "Get closed polls", description = "Returns all polls that have been closed (have a closedAt timestamp)")
    public ResponseEntity<List<Poll>> getClosedPolls() {
        List<Poll> closedPolls = pollRepository.findByClosedAtIsNotNull();
        return ResponseEntity.ok(closedPolls);
    }

    @PostMapping("/{id}/mark-inactive")
    @Operation(summary = "Mark poll as inactive", description = "Marks a poll as inactive (internal use only)")
    public ResponseEntity<?> markPollInactive(
            @PathVariable Long id,
            @RequestHeader(value = "X-Internal-API-Key", required = false) String apiKey) {

        if (internalApiKey == null || !internalApiKey.equals(apiKey)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Invalid API key"));
        }

        try {
            pollService.markPollInactive(id);
            return ResponseEntity.ok(Map.of("message", "Poll marked inactive successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to mark poll inactive: " + e.getMessage()));
        }
    }
}