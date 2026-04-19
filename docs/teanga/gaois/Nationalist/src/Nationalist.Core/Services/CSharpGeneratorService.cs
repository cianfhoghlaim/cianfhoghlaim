using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Formatting;
using Microsoft.Extensions.Options;
using static Microsoft.CodeAnalysis.CSharp.SyntaxFactory;

namespace Nationalist.Core
{
    public class CSharpGeneratorService
    {
        private readonly string _outputPath;

        public CSharpGeneratorService(IOptionsMonitor<NationalistSettings> settings)
        {
            _outputPath = settings.CurrentValue.OutputPath;
        }

        public void WriteCSharp(List<Country> countries, string locale)
        {
            // https://gist.github.com/cmendible/9b8c7d7598f1ab0bc7ab5d24b2622622
            Console.WriteLine("Writing C# file…");

            var outputFile = Path.Combine(_outputPath, $"{locale}/Countries.{locale}.cs");

            var syntaxFactory = CompilationUnit();
            syntaxFactory = syntaxFactory.AddUsings(UsingDirective(ParseName("System")));
            syntaxFactory = syntaxFactory.AddUsings(UsingDirective(ParseName("System.Collections.Generic")));

            var @namespace = NamespaceDeclaration(ParseName($"Nationalist.{locale}")).NormalizeWhitespace();

            var classDeclaration = ClassDeclaration("Countries");
            classDeclaration = classDeclaration.AddModifiers(Token(SyntaxKind.PublicKeyword), Token(SyntaxKind.StaticKeyword));

            var cldrProperty = PropertyDeclaration(
                    GenericName(Identifier("Dictionary")) 
                        .WithTypeArgumentList(
                            TypeArgumentList(
                                SeparatedList<TypeSyntax>(new SyntaxNodeOrToken[]
                                    { 
                                        PredefinedType(Token(SyntaxKind.StringKeyword)),
                                        Token(SyntaxKind.CommaToken),
                                        PredefinedType(Token(SyntaxKind.StringKeyword))
                                    }
                                )
                            )
                        ),
                    Identifier("Cldr")
                ) 
                .WithModifiers(TokenList(Token(SyntaxKind.PublicKeyword), Token(SyntaxKind.StaticKeyword)))
                .WithAccessorList(
                    AccessorList(
                        List(new AccessorDeclarationSyntax[]
                            { 
                                AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken)),
                                AccessorDeclaration(SyntaxKind.SetAccessorDeclaration)
                                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
                            }
                        )
                    )
                )
                .WithInitializer(
                    EqualsValueClause(
                        ObjectCreationExpression(
                            GenericName(Identifier("Dictionary")) 
                                .WithTypeArgumentList(
                                    TypeArgumentList(
                                        SeparatedList<TypeSyntax>(new SyntaxNodeOrToken[]
                                            { 
                                                PredefinedType(Token(SyntaxKind.StringKeyword)),
                                                Token(SyntaxKind.CommaToken),
                                                PredefinedType(Token(SyntaxKind.StringKeyword))
                                            }
                                        )
                                    )
                                )
                            )
                            .WithTrailingTrivia(TriviaList(CarriageReturnLineFeed))
                        .WithInitializer(
                            InitializerExpression(SyntaxKind.CollectionInitializerExpression,
                                SeparatedList<ExpressionSyntax>(
                                    countries.SelectMany(country =>
                                        new SyntaxNodeOrToken[]
                                        {
                                            InitializerExpression(SyntaxKind.ComplexElementInitializerExpression,
                                                SeparatedList<ExpressionSyntax>(
                                                    new SyntaxNodeOrToken[]
                                                    {
                                                        LiteralExpression(SyntaxKind.NumericLiteralExpression, Literal(country.Code)),
                                                            Token(SyntaxKind.CommaToken),
                                                        LiteralExpression(SyntaxKind.StringLiteralExpression, Literal(country.Name))
                                                    }
                                                )
                                            )
                                            .WithOpenBraceToken(Token(TriviaList(CarriageReturnLineFeed, Tab, Tab, Tab), SyntaxKind.OpenBraceToken, TriviaList(Space))),
                                            Token(SyntaxKind.CommaToken)
                                        }
                                    )
                                )
                            )
                            .WithOpenBraceToken(Token(TriviaList(Tab, Tab), SyntaxKind.OpenBraceToken, TriviaList()))
                            .WithCloseBraceToken(Token(TriviaList(CarriageReturnLineFeed, Tab, Tab), SyntaxKind.CloseBraceToken, TriviaList(CarriageReturnLineFeed)))
                        )
                    )
                )
                .WithSemicolonToken(Token(SyntaxKind.SemicolonToken));

            var geoNamesProperty = PropertyDeclaration(
                    GenericName(Identifier("Dictionary")) 
                        .WithTypeArgumentList(
                            TypeArgumentList(
                                SeparatedList<TypeSyntax>(new SyntaxNodeOrToken[]
                                    { 
                                        PredefinedType(Token(SyntaxKind.IntKeyword)),
                                        Token(SyntaxKind.CommaToken),
                                        PredefinedType(Token(SyntaxKind.StringKeyword))
                                    }
                                )
                            )
                        ), 
                    Identifier("GeoNames")
                ) 
                .WithModifiers(TokenList(Token(SyntaxKind.PublicKeyword), Token(SyntaxKind.StaticKeyword)))
                .WithAccessorList(
                    AccessorList(
                        List(new AccessorDeclarationSyntax[]
                            { 
                                AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken)),
                                AccessorDeclaration(SyntaxKind.SetAccessorDeclaration)
                                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
                            }
                        )
                    )
                )
                .WithInitializer(
                    EqualsValueClause(
                        ObjectCreationExpression(
                            GenericName(Identifier("Dictionary")) 
                                .WithTypeArgumentList(
                                    TypeArgumentList(
                                        SeparatedList<TypeSyntax>(new SyntaxNodeOrToken[]
                                            { 
                                                PredefinedType(Token(SyntaxKind.IntKeyword)),
                                                Token(SyntaxKind.CommaToken),
                                                PredefinedType(Token(SyntaxKind.StringKeyword))
                                            }
                                        )
                                    )
                                )
                            )
                            .WithTrailingTrivia(TriviaList(CarriageReturnLineFeed))
                        .WithInitializer(
                            InitializerExpression(SyntaxKind.CollectionInitializerExpression,
                                SeparatedList<ExpressionSyntax>(
                                    countries.SelectMany(country =>
                                        new SyntaxNodeOrToken[]
                                        {
                                            InitializerExpression(SyntaxKind.ComplexElementInitializerExpression,
                                                SeparatedList<ExpressionSyntax>(
                                                    new SyntaxNodeOrToken[]
                                                    {
                                                        LiteralExpression(SyntaxKind.NumericLiteralExpression, Literal((country.GeoNameID is null) ? 0 : country.GeoNameID.GetValueOrDefault())),
                                                            Token(SyntaxKind.CommaToken),
                                                        LiteralExpression(SyntaxKind.StringLiteralExpression, Literal(country.Name))
                                                    }
                                                )
                                            )
                                            .WithOpenBraceToken(Token(TriviaList(CarriageReturnLineFeed, Tab, Tab, Tab), SyntaxKind.OpenBraceToken, TriviaList(Space))),
                                            Token(SyntaxKind.CommaToken)
                                        }
                                    )
                                )
                            )
                            .WithOpenBraceToken(Token(TriviaList(Tab, Tab), SyntaxKind.OpenBraceToken, TriviaList()))
                            .WithCloseBraceToken(Token(TriviaList(CarriageReturnLineFeed, Tab, Tab), SyntaxKind.CloseBraceToken, TriviaList(CarriageReturnLineFeed)))
                        )
                    )
                )
                .WithSemicolonToken(Token(SyntaxKind.SemicolonToken));
            
            classDeclaration = classDeclaration.AddMembers(cldrProperty, geoNamesProperty);
            @namespace = @namespace.AddMembers(classDeclaration);
            syntaxFactory = syntaxFactory.AddMembers(@namespace);

            using (var fileStream = File.CreateText(outputFile))
            {
                var workspace = new AdhocWorkspace();
                var syntaxNode = Formatter.Format(syntaxFactory, workspace);
                var code = syntaxNode.ToFullString();
                fileStream.Write(code);
            }

            Console.WriteLine("C# file written!");
        }
    }
}