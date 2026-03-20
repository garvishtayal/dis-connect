package models

// UpsertUpgradeRequest is the payload for POST /api/upgrade.
type UpsertUpgradeRequest struct {
	UserID        string  `json:"user_id" binding:"required"`
	Upgraded      bool    `json:"upgraded"`
	Feedback      *string `json:"feedback"`
	WillingToPay  *string `json:"willing_to_pay"`
}

// UpgradeRecord is the response returned for GET and POST /api/upgrade.
type UpgradeRecord struct {
	UserID        string  `json:"user_id"`
	Upgraded      bool    `json:"upgraded"`
	Feedback      *string `json:"feedback"`
	WillingToPay  *string `json:"willing_to_pay"`
}
