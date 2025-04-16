import React from 'react';

const TokenUsageDisplay = ({ tokenUsage }) => {
  if (!tokenUsage) return null;
  
  const { daily_usage, daily_limit, daily_remaining, reset_timestamp } = tokenUsage;
  const usagePercentage = Math.min(100, Math.round((daily_usage / daily_limit) * 100));
  
  // Calculate time until reset
  const resetDate = new Date(reset_timestamp * 1000);
  const now = new Date();
  const hoursUntilReset = Math.max(0, Math.round((resetDate - now) / (1000 * 60 * 60)));
  
  // Determine progress bar class based on usage percentage
  let progressBarClass = "token-progress-fill";
  if (usagePercentage > 85) {
    progressBarClass += " critical";
  } else if (usagePercentage > 65) {
    progressBarClass += " warning";
  }
  
  return (
    <div className="token-usage-container">
      <h4 className="token-usage-title">Token Usage</h4>
      
      <div className="token-progress-container">
        <div className="token-progress-bar">
          <div 
            className={progressBarClass}
            style={{ width: `${usagePercentage}%` }}
          />
        </div>
        <div className="token-progress-text">
          {daily_usage.toLocaleString()} / {daily_limit.toLocaleString()} tokens
          <span className="token-progress-percentage">({usagePercentage}%)</span>
        </div>
      </div>
      
      <div className="token-info">
        <div className="token-info-item">
          <span className="token-info-label">Remaining:</span>
          <span className="token-info-value">{daily_remaining.toLocaleString()} tokens</span>
        </div>
        <div className="token-info-item">
          <span className="token-info-label">Resets in:</span>
          <span className="token-info-value">{hoursUntilReset} hours</span>
        </div>
      </div>
    </div>
  );
};

export default TokenUsageDisplay;