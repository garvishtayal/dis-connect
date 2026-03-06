FROM golang:1.22-alpine AS builder

WORKDIR /app

# Go module file first for caching
COPY go.mod ./
RUN go mod download || true

# Copy source and build binary
COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o server ./cmd/api

FROM gcr.io/distroless/base-debian12

WORKDIR /app

COPY --from=builder /app/server .

EXPOSE 8080

ENTRYPOINT ["./server"]


