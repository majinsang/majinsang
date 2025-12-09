#pragma once

void MoveToBlock(int targetBlockX, int targetBlockZ);

void MoveToPosition(double targetX, double targetZ, double threshold = 0.5);

void MoveDirection(char direction, int blocks);
