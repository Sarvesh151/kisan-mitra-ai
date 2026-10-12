"""
===========================================================
Project : Kisan Mitra AI
File    : engine.py
Author  : Sarvesh Kumar
Purpose : Training and validation functions.
===========================================================
"""

import time
import torch


def train_one_epoch(
    model,
    dataloader,
    loss_fn,
    optimizer,
    device
):
    """Train the model for one complete epoch."""

    model.train()

    # Keep frozen EfficientNet features in evaluation mode.
    # This prevents BatchNorm statistics from changing.
    model.features.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    total_batches = len(dataloader)
    start_time = time.time()

    for batch_idx, (images, labels) in enumerate(dataloader):

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        # Forward pass
        outputs = model(images)

        # Loss
        loss = loss_fn(outputs, labels)

        # Backward pass
        loss.backward()

        # Update classifier
        optimizer.step()

        # Metrics
        running_loss += loss.item()

        _, predicted = torch.max(outputs, dim=1)

        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        # Progress every 50 batches
        if (
            (batch_idx + 1) % 50 == 0
            or batch_idx == 0
            or (batch_idx + 1) == total_batches
        ):

            accuracy = (
                100.0 * correct / total
                if total > 0 else 0.0
            )

            elapsed = time.time() - start_time

            print(
                f"Batch {batch_idx + 1}/{total_batches} | "
                f"Loss: {loss.item():.4f} | "
                f"Accuracy: {accuracy:.2f}% | "
                f"Time: {elapsed / 60:.2f} min"
            )

    epoch_loss = running_loss / total_batches

    epoch_accuracy = (
        100.0 * correct / total
        if total > 0 else 0.0
    )

    return epoch_loss, epoch_accuracy


def validate(
    model,
    dataloader,
    loss_fn,
    device
):
    """Validate the model."""

    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    start_time = time.time()

    with torch.no_grad():

        for batch_idx, (images, labels) in enumerate(dataloader):

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = loss_fn(outputs, labels)

            running_loss += loss.item()

            _, predicted = torch.max(outputs, dim=1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            if (
                (batch_idx + 1) % 50 == 0
                or batch_idx == 0
                or (batch_idx + 1) == len(dataloader)
            ):

                accuracy = (
                    100.0 * correct / total
                    if total > 0 else 0.0
                )

                elapsed = time.time() - start_time

                print(
                    f"Validation Batch "
                    f"{batch_idx + 1}/{len(dataloader)} | "
                    f"Accuracy: {accuracy:.2f}% | "
                    f"Time: {elapsed / 60:.2f} min"
                )

    val_loss = running_loss / len(dataloader)

    val_accuracy = (
        100.0 * correct / total
        if total > 0 else 0.0
    )

    return val_loss, val_accuracy