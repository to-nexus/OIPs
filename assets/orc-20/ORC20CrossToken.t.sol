// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.22;

import {CrossToken} from "../src/CrossToken.sol";
import {ORC20Conformance} from "./ORC20Conformance.t.sol";
import {IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

/// @notice Runs the cases against CrossToken compiled from this checkout.
contract ORC20CrossTokenTest is ORC20Conformance {
    CrossToken internal t;

    function setUp() public virtual {
        t = new CrossToken(address(this), 1_000_000_000);
    }

    function token() internal view override returns (IERC20Metadata) {
        return t;
    }
}

/// @notice Runs the cases against the deployed BSC CrossToken; skipped unless ORC20_BSC_URL is set.
contract ORC20CrossTokenBscForkTest is ORC20Conformance {
    function setUp() public {
        forkFromEnv("ORC20_BSC", 56);
    }

    function token() internal pure override returns (IERC20Metadata) {
        return IERC20Metadata(0x6bf62ca91e397B5A7d1D6bCe97D9092065d7A510);
    }
}
