// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol"; //helpful import for ownership purposes..
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    // all addresses in this array are payable addresses..
    uint256 public randomness;
    address payable[] public players;
    address payable public recentWinner;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;

    //OPEN -> 0
    //CLOSED -> 1
    //CALCULATING_WINNER -> 2
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyhash;
    event RequestRandomness(bytes32 requestId);

    // adding additional VRFConsumerBase constructor
    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        // In weis unit (unit of ETH)
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        //$50 minimum
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10; //18 decimals
        //ethUsdPriceFeed will give 10^8 power
        //$50, $2,000 per ETH
        //50/2000 ETH for $50
        //50 * 100000/ 2000
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        // bad practice for random numbers (donot reveal true random number..)
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce, //nonce is predictable (aka, transaction number)
        //             msg.sender, //msg.sender is predictable
        //             block.difficulty, // can be able to manipulated by the miners!
        //             block.timestamp //timestamp is predictable
        //         )
        //     )
        // ) % players.length;

        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
        // above line making a request to chain link node
        emit RequestRandomness(requestId);
    }

    // above requested chainlink node is going to responded with this function
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        // require statement allows the program to flow only if condition is true
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there at!"
        );
        require(_randomness > 0, "random-not-found");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        // Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
