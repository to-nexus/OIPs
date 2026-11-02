// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.22;

import {CrossMintableERC20V2} from "../src/token/CrossMintableERC20V2.sol";
import {ORC20Conformance} from "./ORC20Conformance.t.sol";
import {IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

/// @notice Runs the cases against CrossMintableERC20V2 compiled from this checkout.
contract ORC20CrossMintableERC20V2Test is ORC20Conformance {
    CrossMintableERC20V2 internal t;

    function setUp() public virtual {
        t = new CrossMintableERC20V2(address(this), address(this), "Cross Bridge TEST", "TESTx", 18);
    }

    function token() internal view override returns (IERC20Metadata) {
        return t;
    }

    function test_decimalsSixKeepsRawUnits() public {
        CrossMintableERC20V2 six = new CrossMintableERC20V2(address(this), address(this), "Six", "SIX", 6);
        six.mint(A, 1_234_567);
        assertEq(six.decimals(), 6);
        assertEq(six.balanceOf(A), 1_234_567);
    }

    function test_decimalsZeroIsValid() public {
        CrossMintableERC20V2 zero = new CrossMintableERC20V2(address(this), address(this), "Zero", "ZERO", 0);
        assertEq(zero.decimals(), 0);
    }
}

/// @notice Runs the cases against a deployed ONEchain bridge token; skipped unless ORC20_ONECHAIN_URL is set.
abstract contract ORC20OneChainForkTest is ORC20Conformance {
    function setUp() public {
        forkFromEnv("ORC20_ONECHAIN", 612055);
    }
}

/// @notice Bridge representation of BSC USDT on ONEchain mainnet.
contract ORC20USDTxForkTest is ORC20OneChainForkTest {
    function token() internal pure override returns (IERC20Metadata) {
        return IERC20Metadata(0x1c37d4F44ed3eC86d96868001CfA89e97112a85C);
    }
}

/// @notice Bridge representation of Kaia GHUB on ONEchain mainnet.
contract ORC20GHUBxForkTest is ORC20OneChainForkTest {
    function token() internal pure override returns (IERC20Metadata) {
        return IERC20Metadata(0xB506d82CA638548a597Ac8143217534C524b81dA);
    }
}
