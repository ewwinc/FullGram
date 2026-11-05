package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

var templates = map[string]struct {
	file string
	body string
}{
	"js": {"%s.js", `// @id %[1]s
// @name %[2]s
// @author you
// @version 1.0
// @description What it does
// @permissions menu

fullgram.ui.menu.add({ id: 'count', title: 'Count characters' });
fullgram.on('menuAction', ({ itemId, text }) => {
  if (itemId === 'count') fullgram.toast(String([...text].length) + ' characters');
});
`},
	"ts": {"%s.ts", `// @id %[1]s
// @name %[2]s
// @author you
// @version 1.0
// @description What it does
/// <reference path="fullgram.d.ts" />

fullgram.hooks.before(fullgram.hooks.points.outgoingText, (text: string): string | undefined =>
  text.endsWith('!!') ? text.toUpperCase() : undefined);
`},
	"py": {"%s.py", `# @id %[1]s
# @name %[2]s
# @author you
# @version 1.0
# @description What it does

def shout(text, ctx):
    if text.endswith('!!'):
        return text.upper()
    return None

fullgram.hooks.before('message.outgoing.text', shout)
`},
	"rust": {"%s.rs", `use fullgram_plugin::{hooks, log, manifest};

manifest!(br#"{"id":"%[1]s","name":"%[2]s","author":"you","version":"1.0","description":"What it does"}"#);

#[no_mangle]
pub extern "C" fn fullgram_init() {
    hooks::before(hooks::OUTGOING_TEXT, |text, _ctx| {
        text.ends_with("!!").then(|| text.to_uppercase())
    });
    log("loaded");
}
`},
	"zig": {"%s.zig", `// @manifest {"id":"%[1]s","name":"%[2]s","author":"you","version":"1.0","description":"What it does"}
const fullgram = @import("fullgram.zig");
const std = @import("std");

fn shout(text: []const u8, ctx: fullgram.Context) ?[]const u8 {
    _ = ctx;
    if (!std.mem.endsWith(u8, text, "!!")) return null;
    return fullgram.upper(text);
}

export fn fullgram_init() void {
    fullgram.hooks.before(fullgram.hooks.outgoing_text, shout);
    fullgram.log("loaded");
}
`},
	"as": {"%s.as.ts", `// @manifest {"id":"%[1]s","name":"%[2]s","author":"you","version":"1.0","description":"What it does"}
export { fullgram_alloc, fullgram_free, fullgram_dispatch } from "./fullgram";
import { log, before, OUTGOING_TEXT } from "./fullgram";

export function fullgram_init(): void {
  before(OUTGOING_TEXT, (text: string, peerId: string): string | null =>
    text.endsWith("!!") ? text.toUpperCase() : null);
  log("loaded");
}
`},
	"go": {"%s.go", `// @manifest {"id":"%[1]s","name":"%[2]s","author":"you","version":"1.0","description":"What it does"}
package main

import (
	"strings"

	"github.com/FullGram/fullgram-sdk/ayu"
)

//export fullgram_init
func fullgramInit() {
	fullgram.Before(fullgram.OutgoingText, func(text string, ctx fullgram.Context) *string {
		if !strings.HasSuffix(text, "!!") {
			return nil
		}
		upper := strings.ToUpper(text)
		return &upper
	})
	fullgram.Log("loaded")
}

func main() {}
`},
}

func scaffold(name, language string) error {
	template, ok := templates[language]
	if !ok {
		return fmt.Errorf("unknown language %q (js, ts, py, rust, zig, as, go)", language)
	}
	id := strings.ToLower(strings.Map(func(r rune) rune {
		if r >= 'a' && r <= 'z' || r >= 'A' && r <= 'Z' || r >= '0' && r <= '9' || r == '-' || r == '_' {
			return r
		}
		return '-'
	}, name))
	file := fmt.Sprintf(template.file, id)
	if _, err := os.Stat(file); err == nil {
		return fmt.Errorf("%s already exists", file)
	}
	if err := os.WriteFile(file, []byte(fmt.Sprintf(template.body, id, name)), 0o644); err != nil {
		return err
	}
	fmt.Printf("created %s\n", filepath.Clean(file))
	switch language {
	case "js", "py":
		fmt.Println("next: fullgram check " + file + " && fullgram dev " + file)
	case "ts":
		fmt.Println("next: copy sdk/typescript/fullgram.d.ts here, build with esbuild, or send the .ts to the cloud build")
	default:
		fmt.Println("next: build with the SDK in sdk/, then `fullgram pack` and `fullgram check` (or use the cloud build)")
	}
	return nil
}
