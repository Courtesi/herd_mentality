package dev.wenslo.trueshotodds.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;

@Entity
@Table(name = "polls")
@Data
public class Poll {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 500)
    private String question;

    @Column(length = 2000)
    private String description;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "ends_at", nullable = false)
    private LocalDateTime endsAt;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;

    @Column(name = "option_a_text", nullable = false, length = 255)
    private String optionAText;

    @Column(name = "option_a_votes", nullable = false)
    private Integer optionAVotes = 0;

    @Column(name = "option_b_text", nullable = false, length = 255)
    private String optionBText;

    @Column(name = "option_b_votes", nullable = false)
    private Integer optionBVotes = 0;

    @Column(name = "market_ticker", nullable = false)
    private String marketTicker;

    @Column(name = "series_ticker", nullable = false)
    private String seriesTicker;

    @Column(name = "closed_at")
    private LocalDateTime closedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (endsAt == null) {
            endsAt = createdAt.plusDays(7); // Default 7 days
        }
    }

    // Constructors
    public Poll() {}

    public Poll(String question, String description, String optionAText, String optionBText, String marketTicker, String seriesTicker) {
        this.question = question;
        this.description = description;
        this.optionAText = optionAText;
        this.optionBText = optionBText;
        this.isActive = true;
        this.optionAVotes = 0;
        this.optionBVotes = 0;
        this.marketTicker = marketTicker;
        this.seriesTicker = seriesTicker;
    }
}