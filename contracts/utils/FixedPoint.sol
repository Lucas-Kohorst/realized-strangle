/**
 * Copyright (C) 2020  moodysalem
 * Modifications Copyright (C) 2020  Will Shahda
 * 2020-06-03: Update for use as a general purpose library
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

// SPDX-License-Identifier: GPL-3.0-or-later

pragma solidity >=0.4.0;

import {Babylonian} from "./Babylonian.sol";

library FixedPoint {
    struct uq64x96 { // solhint-disable-line contract-name-camelcase
        uint _x;
    }

    uint8 private constant _M = 64;
    uint8 private constant _N = 96;
    uint private constant _Q64 = uint(1) << _M;
    uint private constant _Q96 = uint(1) << _N;

    // encode a uint192 as a UQ64*96
    function encode(uint192 x) internal pure returns (uq64x96 memory) {
        return uq64x96(uint(x) << _N);
    }

    // divide a UQ64*96 by a uint192, returning a UQ64*96
    function div(uq64x96 memory self, uint192 x) internal pure returns (uq64x96 memory) {
        require(x != 0, "FixedPoint: DIV_BY_ZERO");
        return uq64x96(self._x / uint(x));
    }

    // multiply a UQ64*96 by a uint, returning a UQ64*96
    // reverts on overflow
    function mul(uq64x96 memory self, uint y) internal pure returns (uq64x96 memory) {
        uint z;
        require(
            y == 0 || (z = self._x * y) / y == self._x,
            "FixedPoint: MUL_OVERFLOW"
        );
        return uq64x96(z);
    }

    // returns a UQ64*96 which represents the ratio of the numerator to the denominator
    // equivalent to encode(numerator).div(denominator)
    function fraction(uint192 numerator, uint192 denominator)
        internal
        pure
        returns (uq64x96 memory)
    {
        require(denominator > 0, "FixedPoint: DIV_BY_ZERO");
        return uq64x96((uint(numerator) << _N) / denominator);
    }

    // decode a UQ64*96 into a uint192 by truncating after the radix point
    function decode(uq64x96 memory self) internal pure returns (uint192) {
        return uint192(self._x >> _N);
    }

    // take the reciprocal of a UQ64*96
    function reciprocal(uq64x96 memory self) internal pure returns (uq64x96 memory) {
        require(self._x != 0, "FixedPoint: ZERO_RECIPROCAL");
        return uq64x96(_Q96 / self._x * _Q96);
    }

    // square root of a UQ64*96
    function sqrt(uq64x96 memory self) internal pure returns (uq64x96 memory) {
        return uq64x96(Babylonian.sqrt(self._x) << 32);
    }
}