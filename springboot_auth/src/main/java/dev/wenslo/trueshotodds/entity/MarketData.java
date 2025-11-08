package dev.wenslo.trueshotodds.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

/**
 * Entity representing market data from Kalshi API.
 * Used by FastAPI for caching market metadata.
 */
@Entity
@Table(name = "market_data")
@Data
public class MarketData {

    @Id
    @Column(name = "ticker", nullable = false, length = 50)
    private String ticker;

    @Column(name = "data", nullable = false, columnDefinition = "JSON")
    @JdbcTypeCode(SqlTypes.JSON)
    private String data;

    @Column(name = "created_at", nullable = false, updatable = false,
            insertable = false, columnDefinition = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    private LocalDateTime createdAt;
}
