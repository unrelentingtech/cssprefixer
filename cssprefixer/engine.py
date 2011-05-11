# CSSPrefixer
# Copyright 2010 MyFreeWeb <me@myfreeweb.ru>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cssutils

import re
from rules import rules as tr_rules
from rules import prefixRegex

def magic(ruleset, debug, minify):
    if hasattr(ruleset, 'style'): # Comments don't
        ruleSet = set(); rules = list()
        children = list(ruleset.style.children())
        ruleset.style = cssutils.css.CSSStyleDeclaration()#clear out the styles that were there
        for rule in children:
            if not hasattr(rule, 'name'):#comments don't have name
                rules.append(rule)
                continue
            name = prefixRegex.sub('', rule.name)
            if name in tr_rules:
                rule.name = name
            if rule.cssText in ruleSet:
                continue
            ruleSet.add(rule.cssText)
            rules.append(rule)

        ruleset.style.seq._readonly = False
        for rule in rules:
            if not hasattr(rule, 'name'):
                ruleset.style.seq.append(rule, 'Comment')
                continue
            processor = None
            try:#try except so if anything goes wrong we don't lose the original property
                if rule.name in tr_rules:
                    processor = tr_rules[rule.name](rule)
                    [ruleset.style.seq.append(prop, 'Property') for prop in processor.get_prefixed_props() if prop]
                #always add the original rule
                if processor and hasattr(processor, 'get_base_prop'):
                    ruleset.style.seq.append(processor.get_base_prop(), 'Property')
                else:
                    ruleset.style.seq.append(rule, 'Property')
            except:
                if debug:
                    print 'warning with ' + str(rule)
                ruleset.style.seq.append(rule, 'Property')
        ruleset.style.seq._readonly = True
    elif hasattr(ruleset, 'cssRules'):
        for subruleset in ruleset:
            magic(subruleset, debug, minify)
    cssText = ruleset.cssText
    if not cssText:#blank rules return None so return an empty string
        return
    if minify or not hasattr(ruleset, 'style'):
        return unicode(cssText)
    return unicode(cssText)+'\n'

def process(string, debug=False, minify=False, **prefs):
    loglevel = 'info' if debug else 'error'
    parser = cssutils.CSSParser(loglevel=loglevel)
    if minify:
        cssutils.ser.prefs.useMinified()
    else:
        cssutils.ser.prefs.useDefaults()
    #use the passed in prefs
    for key, value in prefs.iteritems():
        if hasattr(cssutils.ser.prefs, key):
            cssutils.ser.prefs.__dict__[key] = value

    results = []
    sheet = parser.parseString(string)
    for ruleset in sheet.cssRules:
        cssText = magic(ruleset, debug, minify)
        if cssText:
            results.append(cssText)

    #format with newlines based on minify
    joinStr = '' if minify else '\n'

    # Not using sheet.cssText - it's buggy:
    # it skips some prefixed properties.
    return joinStr.join(results).rstrip()

__all__ = ('process')
