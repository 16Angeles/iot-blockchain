// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TemperatureStorage {
    struct TemperatureRecord {
        uint timestamp;
        uint temperature;
    }

    TemperatureRecord[] public records;

    event TemperatureRecorded(uint timestamp, uint temperature);

    function recordTemperature(uint _temperature) public {
        uint _timestamp = block.timestamp; 

        records.push(TemperatureRecord(_timestamp, _temperature));

        emit TemperatureRecorded(_timestamp, _temperature);
    }

    function getTemperatureRecord(uint index) public view returns (uint timestamp, uint temperature) {
        require(index < records.length, "Record does not exist");
        TemperatureRecord memory record = records[index];
        return (record.timestamp, record.temperature);
    }

    function getRecordCount() public view returns (uint) {
        return records.length;
    }
}
