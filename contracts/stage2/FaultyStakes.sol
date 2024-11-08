// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FaultyStakes {
    struct Unstake {
        uint256 amount;
        uint256 releaseTime;
    }

    struct Stake {
        uint256 amount;
        uint256 firstUnstakeIndex;
        Unstake[] unstakes;
    }

    uint256 public constant MIN_STAKE = 0.1 ether;
    uint256 public constant SLASH_PENALTY_BASE = 10 ** 12;
    uint256 public constant MAX_UNSTAKES = 10;
    uint256 public constant UNSTAKE_DELAY = 1 days;

    mapping(address => Stake) public stakes;
    mapping(address => uint256) public rewardPoints;
    uint256 public reserve;
    address public owner;

    error EmptyValue();
    error NotAuthorized();
    error NotEnoughStake();
    error InsufficientStake();
    error TooManyUnstakes();
    error UnstakeNotAvailable();
    error InsufficientValueLocked();
    error TransferFailed();
    error ReserveEmpty();

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotAuthorized();
        _;
    }

    function stake() external payable {
        if (msg.value == 0) revert EmptyValue();
        Stake storage userStake = stakes[msg.sender];
        userStake.amount += msg.value;
    }

    function play(uint256 guessedValue) external {
        Stake storage userStake = stakes[msg.sender];
        if (userStake.amount < MIN_STAKE) revert NotEnoughStake();
        uint256 correctAnswer = block.timestamp % 100;
        if (correctAnswer != guessedValue) {
            uint256 penalty = (SLASH_PENALTY_BASE * 100) / correctAnswer;
            _slash(msg.sender, penalty);
        } else {
            rewardPoints[msg.sender] += 1;
        }
    }

    function unstake(uint256 amount) external {
        Stake storage userStake = stakes[msg.sender];
        if (
            userStake.unstakes.length - userStake.firstUnstakeIndex ==
            MAX_UNSTAKES
        ) revert TooManyUnstakes();
        if (userStake.amount < amount) revert InsufficientStake();

        userStake.amount -= amount;
        userStake.unstakes.push(
            Unstake(amount, block.timestamp + UNSTAKE_DELAY)
        );
    }

    function withdraw(uint256 amount) external {
        Stake storage userStake = stakes[msg.sender];
        if (userStake.unstakes.length == 0) revert UnstakeNotAvailable();
        uint256 amountToWithdraw = 0;
        uint256 startIndex = userStake.firstUnstakeIndex;

        while (startIndex < userStake.unstakes.length) {
            Unstake storage currentUnstake = userStake.unstakes[startIndex];
            if (block.timestamp < currentUnstake.releaseTime)
                revert UnstakeNotAvailable();

            uint256 availableAmount = currentUnstake.amount;

            if (availableAmount <= amount - amountToWithdraw) {
                amountToWithdraw += availableAmount;
                currentUnstake.amount = 0;
                startIndex += 1;
            } else {
                uint256 remainingAmount = amount - amountToWithdraw;
                currentUnstake.amount -= remainingAmount;
                amountToWithdraw += remainingAmount;
                break;
            }
        }

        userStake.firstUnstakeIndex = startIndex;
        if (amountToWithdraw != amount) revert InsufficientValueLocked();
        (bool success, ) = payable(msg.sender).call{value: amountToWithdraw}(
            ""
        );
        if (!success) revert TransferFailed();
    }

    function withdrawReserves() external onlyOwner {
        if (reserve == 0) revert ReserveEmpty();
        uint256 amount = reserve;
        reserve = 0;

        (bool success, ) = payable(owner).call{value: amount}("");
        if (!success) revert TransferFailed();
    }

    function _slash(address user, uint256 penalty) internal {
        Stake storage userStake = stakes[user];

        if (userStake.amount >= penalty) {
            userStake.amount -= penalty;
            reserve += penalty;
        } else {
            uint256 remainingPenalty = penalty - userStake.amount;
            reserve += userStake.amount;
            userStake.amount = 0;

            while (remainingPenalty > 0 && userStake.unstakes.length > 0) {
                Unstake storage latestUnstake = userStake.unstakes[
                    userStake.unstakes.length - 1
                ];

                if (latestUnstake.amount <= remainingPenalty) {
                    remainingPenalty -= latestUnstake.amount;
                    reserve += latestUnstake.amount;
                    userStake.unstakes.pop();
                } else {
                    latestUnstake.amount -= remainingPenalty;
                    reserve += remainingPenalty;
                    remainingPenalty = 0;
                }
            }

            if (remainingPenalty > 0) revert InsufficientValueLocked();
        }
    }
}
